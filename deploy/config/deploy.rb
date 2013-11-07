#
# Put here shared configuration shared among all children
#
# Read more about configurations:
# https://github.com/railsware/capistrano-multiconfig/README.md

# Configuration example for layout like:
# config/deploy/{NAMESPACE}/.../#{PROJECT_NAME}/{STAGE_NAME}.rb

set :scm, :git

set :git_shallow_clone, 1

set :deploy_via, :export

#set :branch, lambda { Capistrano::CLI.ui.ask "SCM branch: " }
set :branch, ENV['BRANCH'] || "master"

#set(:application) { config_name.split(':').reverse[1] }

set :application, 'iowacode'

set(:site) { config_name.split(':')[0] }

set(:stage) { config_name.split(':').last }

set(:rake) { use_bundle ? "bundle exec rake" : "rake" }

set :repository,  "git@github.com:opengovfoundation/iowacode.git"

set :user, "deploy"
set :group, "staff"
set :use_sudo, false

set(:deploy_to) { "/var/www/releases/#{application}/#{site}/#{stage}" }

# Don't do the normal timestamp update, as it uses Rails paths.
set :normalize_asset_timestamps, false

# We're not using any of the other shared folders atm, so remove them.
set :shared_children, []

# set :calendar_username, ''
#
# set :calendar_password, 'qwery123456'
#
# set(:calendar_name) { "mycompany-#{stage}" }
#
# after 'deploy' do
#   set :calendar_event_title, "[DEPLOYED] #{application} #{branch}: #{real_revision}"
#   top.calendar.create_event
# end

after "deploy:finalize_update" do
  run "ln -nfs #{shared_path}/includes/config.inc.php #{release_path}/includes/config.inc.php"
#  run "ln -nfs #{shared_path}/data #{release_path}/htdocs/admin/xml"
  run "chmod g+rw #{release_path}/htdocs/admin/xml"
  # Remove the existing downloads dir.
  run "rm -R #{release_path}/htdocs/downloads"
  run "ln -nfs #{shared_path}/downloads #{release_path}/htdocs/downloads"
  run "ln -nfs #{shared_path}/data #{release_path}/htdocs/admin/data"
  run "chmod g+rw #{release_path}/htdocs/admin/data"
  run "chmod g+rw #{release_path}/htdocs/sitemap.xml"
  run "chmod g+rw #{release_path}/htdocs/.htaccess"

end

# Setup the shared folders.  Since we don't symlink these directly,
# we can't just throw them in :shared_children.
after "deploy:setup" do
  run "mkdir #{shared_path}/data"
  run "mkdir #{shared_path}/downloads"
  run "chmod g+rw #{shared_path}/downloads"
  run "mkdir #{shared_path}/includes"
end

