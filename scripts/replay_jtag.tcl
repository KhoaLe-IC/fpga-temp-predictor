# quartus_stp -t scripts/replay_jtag.tcl temperature|temperature_speed|temperature_resource|weather_speed|weather_resource ?hardware_name? ?device_name?
package require ::quartus::insystem_source_probe
proc probe_value {} {
 set h [string trim [read_probe_data -instance_index 0 -value_in_hex]]
 if {![regexp {^[0-9a-fA-F]+$} $h]} {error "Invalid/unknown JTAG probe: $h"}
 return [expr 0x$h]
}
proc wait_probe {mask expected} {
 for {set i 0} {$i<500} {incr i} {
  set p [probe_value]
  if {($p & $mask)==$expected} {
   after 1
   set q [probe_value]
   if {$q==$p} {return $q}
  }
  after 5
 }
 error "JTAG timeout waiting for stable acknowledgement/status; check CLOCK_50, KEY0 and programming file"
}
proc signed_raw {v width} {
 set mask [expr {(1<<$width)-1}];set v [expr {$v & $mask}]
 if {$v & (1<<($width-1))} {set v [expr {$v-(1<<$width)}]}
 return $v
}
proc main {} {
 global quartus
 set args $quartus(args)
 if {[llength $args]<1 || [llength $args]>3} {error "Usage: replay_jtag.tcl temperature|temperature_speed|temperature_resource|weather_speed|weather_resource ?hardware? ?device?"}
 set variant [lindex $args 0]
 if {$variant ni {temperature temperature_speed temperature_resource weather_speed weather_resource}} {error "Unknown variant $variant"}
 set root [file normalize [file join [file dirname [info script]] ..]]
 set weather [string match "weather_*" $variant];set shared [string match "*_resource" $variant]
 set hardware [get_hardware_names]
 if {[llength $args]>1} {set hardware [list [lindex $args 1]]}
 if {[llength $hardware]!=1} {error "Expected exactly one USB-Blaster; found $hardware. Supply its exact name explicitly."}
 set hardware [lindex $hardware 0]
 set devices [get_device_names -hardware_name $hardware]
 if {[llength $args]>2} {set devices [list [lindex $args 2]]}
 if {[llength $devices]!=1 || ![string match {*EP2C35*} [lindex $devices 0]]} {error "Select the EP2C35 device explicitly; detected: $devices"}
 set device [lindex $devices 0]
 set nodes [get_insystem_source_probe_instance_info -hardware_name $hardware -device_name $device]
 set found 0
 foreach node $nodes {
  if {[lindex $node 0]==0 && [lindex $node 1]==128 && [lindex $node 2]==256 && [lindex $node 3] eq "FCST"} {set found 1}
 }
 if {!$found} {error "FCST source/probe node (128/256 bits, index 0) not found: $nodes. Program a JTAG project, not a UART project."}
 puts "Hardware: $hardware\nDevice: $device\nVariant: $variant\nNode: $nodes"
 start_insystem_source_probe -hardware_name $hardware -device_name $device
 set p [probe_value]
 if {(($p>>224)&0xffffffff)!=0x46504741 || (($p>>166)&1)!=$weather || (($p>>167)&1)!=$shared} {error "JTAG design identity mismatch"}
 # Reset through JTAG; no physical button or external serial port is required.
 write_source_data -instance_index 0 -value 2 -value_in_hex
 wait_probe [expr {1<<165}] [expr {1<<165}]
 write_source_data -instance_index 0 -value 0 -value_in_hex
 set p [wait_probe [expr {(1<<165)|(1<<160)|(0xffffffff<<128)}] 0]
 set vf [expr {$weather ? "weather.txt" : "temperature.txt"}]
 set fd [open [file join $root hardware jtag vectors $vf] r]
 set outpath [file join $root docs reports physical_jtag_${variant}.csv]
 if {[info exists ::env(FPGA_JTAG_CSV)]} {set outpath [file normalize $::env(FPGA_JTAG_CSV)]}
 set out [open $outpath w];puts $out "sample_index,accepted_count,forecast_count,forecast_raw,forecast_physical,probe_hex,match"
 set n 0;set checked 0
 set replay_code [catch {
  while {[gets $fd line]>=0} {
   if {[llength $line]!=5} {error "Malformed JTAG vector line"}
   lassign $line stage commit expected_count expected_fc result
   write_source_data -instance_index 0 -value $stage -value_in_hex
   after 1
   write_source_data -instance_index 0 -value $commit -value_in_hex
   set request [expr {([expr 0x$commit]&1)<<160}]
   set p [wait_probe [expr {(1<<160)|(1<<161)}] $request]
   set count [expr {($p>>128)&65535}];set fc [expr {($p>>144)&65535}]
   if {$count!=$expected_count || $fc!=$expected_fc} {error "Counter mismatch at sample $n: accepted=$count forecasts=$fc"}
   set result [expr 0x$result];set match warmup;set raw {};set physical {}
   if {$expected_fc>0} {
    if {!(($p>>162)&1)} {error "Missing forecast flag"}
    if {$weather} {
     if {($p&((1<<108)-1))!=($result&((1<<108)-1))} {error "Weather forecast mismatch at sample $n"}
     set angle [expr {($p>>108)&262143}];set expected_angle [expr {($result>>108)&262143}]
     set delta [expr {abs($angle-$expected_angle)}];if {$delta>46080} {set delta [expr {92160-$delta}]}
     if {$delta>5} {error "Direction angle mismatch at sample $n"}
     set defined [expr {(($result>>72)&262143)!=0 || (($result>>90)&262143)!=0}]
     if {(($p>>163)&1)!=$defined} {error "Direction-defined flag mismatch"}
     for {set c 0} {$c<6} {incr c} {set v [signed_raw [expr {$p>>(18*$c)}] 18];lappend raw $v;lappend physical [format %.6f [expr {$v/256.0}]]}
     lappend raw $angle;lappend physical [format %.6f [expr {$angle/256.0}]]
    } else {
     set raw [signed_raw $p 16]
     if {($p&65535)!=($result&65535)} {error "Temperature forecast mismatch at sample $n"}
     set physical [format %.6f [expr {$raw/256.0}]]
    }
    set match True;incr checked
    puts "sample=$n forecast=$physical match=True"
   } elseif {($p>>162)&1} {error "Unexpected forecast during warmup"}
   set hex [string trim [read_probe_data -instance_index 0 -value_in_hex]]
   puts $out "$n,$count,$fc,$raw,$physical,$hex,$match";flush $out;incr n
  }
  if {$n!=128 || $checked!=104} {error "Incomplete JTAG replay: inputs=$n forecasts=$checked"}
 } replay_message]
 close $fd;close $out
 if {$replay_code} {error $replay_message}
 puts "PASS PHYSICAL JTAG $variant: inputs=$n forecasts=$checked; CSV=$outpath"
}
set code [catch {main} message options]
catch {end_insystem_source_probe}
if {$code} {puts stderr "FAIL JTAG: $message";exit 1}
