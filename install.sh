# add compass to the path
export PATH=$PATH:/tmp/gems/bin
gem install compass
./node_modules/bower/bin/bower install
./node_modules/grunt-cli/bin/grunt build
