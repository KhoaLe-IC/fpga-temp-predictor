# One host command: send a 25-frame window to the DE2 and leave the single forecast on the LCD.
#   quartus_stp -t versions/weather_v2/lcd/host/send_window.tcl window.csv ?hardware_name? ?device_name?
# window.csv: header + 25 rows, oldest first: timestamp,T2M,PS,RH2M,WS10M,WD10M (C, kPa, %, m/s, degrees).
# The last row is time t; the forecast is for t + 3 h. Make one with: python3 lcd_reference.py window --end ...
# Protocol and field map are those of hardware/jtag/README.md (unchanged mailbox).
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
 error "JTAG timeout waiting for acknowledgement; check CLOCK_50, KEY0 and the programmed .sof"
}
proc signed_raw {v width} {
 set mask [expr {(1<<$width)-1}];set v [expr {$v & $mask}]
 if {$v & (1<<($width-1))} {set v [expr {$v-(1<<$width)}]}
 return $v
}
# Round half away from zero to Q8, as in make_vectors.py / lcd_reference.py.
proc q8 {x} {
 if {![string is double -strict $x]} {error "Not a number: '$x'"}
 set m [expr {int(floor(abs($x)*256.0+0.5))}]
 if {$m>131071} {error "Value $x does not fit signed 18-bit Q8 (|x| < 512); check the units (C, kPa, %, m/s, degrees)"}
 return [expr {$x<0 ? -$m : $m}]
}
proc read_window {path} {
 set fd [open $path r];set rows {}
 gets $fd header
 while {[gets $fd line]>=0} {
  set line [string trim $line]
  if {$line eq ""} continue
  set f [split $line ,]
  if {[llength $f]!=6} {error "Expected timestamp,T2M,PS,RH2M,WS10M,WD10M: $line"}
  lappend rows $f
 }
 close $fd
 if {[llength $rows]!=25} {error "Window must have exactly 25 frames, found [llength $rows]"}
 return $rows
}
proc payload {row} {
 lassign $row ts t p rh ws wd
 set r [expr {$wd*(3.141592653589793/180.0)}]
 set word 0;set c 0
 foreach v [list [q8 $t] [q8 $p] [q8 $rh] [q8 $ws] [q8 [expr {cos($r)}]] [q8 [expr {sin($r)}]]] {
  set word [expr {$word | (($v & 0x3FFFF) << (18*$c))}];incr c
 }
 return $word
}
# Same text rules as weather_lcd_text.v.
proc lcd_lines {t p h w angle defined} {
 set t10 [expr {min((abs($t)*10+128)>>8,999)}]
 set p100 [expr {(max($p,0)*100+128)>>8}]
 set hp [expr {(max($h,0)+128)>>8}]
 set w10 [expr {min((max($w,0)*10+128)>>8,999)}]
 set deg [expr {($angle+128)>>8}];if {$deg>=360} {set deg 0}
 set l1 [format "T%s%2d.%dC P%3d.%02d " [expr {$t<0?"-":"+"}] [expr {$t10/10}] [expr {$t10%10}] [expr {$p100/100}] [expr {$p100%100}]]
 if {$defined} {set d [format %3d $deg]} else {set d "---"}
 set l2 [format "H%3d%% W%2d.%d D%s" $hp [expr {$w10/10}] [expr {$w10%10}] $d]
 return [list $l1 $l2]
}

proc main {} {
 global quartus
 set args $quartus(args)
 if {[llength $args]<1 || [llength $args]>3} {error "Usage: send_window.tcl window.csv ?hardware? ?device?"}
 set rows [read_window [lindex $args 0]]
 set hardware [get_hardware_names]
 if {[llength $args]>1} {set hardware [list [lindex $args 1]]}
 if {[llength $hardware]!=1} {error "Expected exactly one USB-Blaster; found $hardware. Supply its exact name."}
 set hardware [lindex $hardware 0]
 set devices [get_device_names -hardware_name $hardware]
 if {[llength $args]>2} {set devices [list [lindex $args 2]]}
 if {[llength $devices]!=1 || ![string match {*EP2C35*} [lindex $devices 0]]} {error "Select the EP2C35 device explicitly; detected: $devices"}
 set device [lindex $devices 0]
 set found 0
 foreach node [get_insystem_source_probe_instance_info -hardware_name $hardware -device_name $device] {
  if {[lindex $node 0]==0 && [lindex $node 1]==128 && [lindex $node 2]==256 && [lindex $node 3] eq "FCST"} {set found 1}
 }
 if {!$found} {error "FCST source/probe node not found. Program weather_lcd.sof first."}
 start_insystem_source_probe -hardware_name $hardware -device_name $device
 set p [probe_value]
 if {(($p>>224)&0xffffffff)!=0x46504741 || (($p>>166)&1)!=1 || (($p>>167)&1)!=0} {error "JTAG design identity mismatch (expected the parallel weather design)"}

 # Fresh history: reset through JTAG (the LCD keeps the previous forecast until the new one arrives).
 write_source_data -instance_index 0 -value 2 -value_in_hex
 wait_probe [expr {1<<165}] [expr {1<<165}]
 write_source_data -instance_index 0 -value 0 -value_in_hex
 wait_probe [expr {(1<<165)|(1<<160)|(0xffffffff<<128)}] 0

 set toggle 0;set n 0
 foreach row $rows {
  set word [expr {[payload $row] << 2}]
  write_source_data -instance_index 0 -value [format %032llx [expr {$word|$toggle}]] -value_in_hex
  after 1
  set toggle [expr {1-$toggle}]
  write_source_data -instance_index 0 -value [format %032llx [expr {$word|$toggle}]] -value_in_hex
  set p [wait_probe [expr {(1<<160)|(1<<161)}] [expr {$toggle<<160}]]
  incr n
 }
 set accepted [expr {($p>>128)&65535}];set forecasts [expr {($p>>144)&65535}]
 if {$accepted!=25 || $forecasts!=1 || !(($p>>162)&1)} {error "Expected 25 accepted frames and 1 forecast; got $accepted / $forecasts"}

 set names {"temperature C" "pressure kPa" "humidity %" "wind speed m/s" "direction cos" "direction sin"}
 set raw {}
 puts "Window: [lindex [lindex $rows 0] 0] .. [lindex [lindex $rows end] 0]  (forecast for +3 h)"
 for {set c 0} {$c<6} {incr c} {
  set v [signed_raw [expr {$p>>(18*$c)}] 18];lappend raw $v
  puts [format "  %-15s %10.4f   (raw %d)" [lindex $names $c] [expr {$v/256.0}] $v]
 }
 set angle [expr {($p>>108)&262143}];set defined [expr {($p>>163)&1}]
 puts [format "  %-15s %10.4f   (raw %d, defined=%d)" "direction deg" [expr {$angle/256.0}] $angle $defined]
 lassign [lcd_lines {*}[lrange $raw 0 3] $angle $defined] l1 l2
 puts "LCD now holds:\n  |$l1|\n  |$l2|"
}
set code [catch {main} message]
catch {end_insystem_source_probe}
if {$code} {puts stderr "FAIL: $message";exit 1}
