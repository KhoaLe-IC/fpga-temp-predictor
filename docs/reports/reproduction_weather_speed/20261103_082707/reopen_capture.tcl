package require ::quartus::stp
set path [file normalize [lindex $quartus(args) 0]]
open_session -name $path
puts "REOPENED STP: $path"
close_session
puts "REOPEN/CLOSE SUCCESS"
