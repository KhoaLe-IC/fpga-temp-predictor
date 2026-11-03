package require ::quartus::project
puts "TALKBACK before: [get_user_option -name TALKBACK_ENABLED]"
set_user_option -name TALKBACK_ENABLED on
puts "TALKBACK after: [get_user_option -name TALKBACK_ENABLED]"
