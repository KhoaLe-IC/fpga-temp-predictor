"""Exercise the real Tcl replay under mocked JTAG APIs, never writing physical evidence."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[1];B=R/'hardware/jtag/build/host_mock';B.mkdir(parents=True,exist_ok=True)
mock=r'''
package require ::quartus::insystem_source_probe
set variant [lindex $quartus(args) 0]
set scenario [lindex $quartus(args) 1]
set root [file normalize [file join [file dirname [info script]] ../../../..]]
set weather [string match "weather_*" $variant];set shared [string match "*_resource" $variant]
set fd [open [file join $root hardware jtag vectors [expr {$weather ? "weather.txt" : "temperature.txt"}]] r]
set rows [split [string trim [read $fd]] \n];close $fd
set row_index 0;set toggle 0
set base [expr {(0x46504741<<224)|($weather<<166)|($shared<<167)|(1<<164)}]
set mock_probe $base
proc get_hardware_names {} {return [list "MOCK USB-Blaster"]}
proc get_device_names {args} {return [list "@1: EP2C35 (MOCK)"]}
proc get_insystem_source_probe_instance_info {args} {return {{0 128 256 FCST}}}
proc start_insystem_source_probe {args} {}
proc end_insystem_source_probe {} {}
proc hex_integer {v} {
 if {$v==0} {return 0};set h {};set digits 0123456789abcdef
 while {$v>0} {set h "[string index $digits [expr {$v&15}]]$h";set v [expr {$v>>4}]}
 return $h
}
proc read_probe_data {args} {global mock_probe;return [hex_integer $mock_probe]}
proc write_source_data {args} {
 global base mock_probe toggle row_index rows scenario
 set hex [lindex $args [expr {[lsearch -exact $args -value]+1}]];set v [expr 0x$hex]
 if {$v&2} {set toggle [expr {$v&1}];set row_index 0;set mock_probe [expr {$base|(1<<165)|($toggle<<160)}];return}
 if {($mock_probe>>165)&1} {set mock_probe [expr {$base|($toggle<<160)}];return}
 if {($v&1)!=$toggle} {
  lassign [lindex $rows $row_index] stage commit count fc result
  if {$v!=[expr 0x$commit]} {error "Wrong source packing or request sequence"}
  set result [expr 0x$result];set toggle [expr {$v&1}]
  set defined [expr {(($result>>72)&262143)!=0 || (($result>>90)&262143)!=0}]
  set mock_probe [expr {$base|($toggle<<160)|($count<<128)|($fc<<144)}]
  if {$fc>0} {set mock_probe [expr {$mock_probe|$result|(1<<162)|($defined<<163)}]}
  if {$scenario eq "corrupt" && $fc>0} {set mock_probe [expr {$mock_probe^1}]}
  incr row_index
 }
}
# All generated CSVs are MOCK output. Never create docs/reports/physical_jtag_*.csv.
set mock_csv [file join $root hardware jtag build host_mock mock_output.csv]
rename open actual_open
proc open {path args} {
 global mock_csv
 if {[string match {*physical_jtag_*.csv} $path]} {set path $mock_csv}
 return [eval [linsert $args 0 actual_open $path]]
}
# Avoid real polling delays in the transport mock.
rename after actual_after
proc after {args} {}
set quartus(args) [list $variant]
source [file join $root scripts replay_jtag.tcl]
'''
(B/'mock.tcl').write_text(mock)
for variant,scenario,expected in [('temperature','good',True),('temperature_speed','good',True),('temperature_resource','good',True),('weather_speed','good',True),('weather_resource','good',True),('temperature','corrupt',False),('weather_speed','corrupt',False)]:
 p=subprocess.run(['quartus_stp','-t',str(B/'mock.tcl'),variant,scenario],cwd=R,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (B/f'{variant}_{scenario}.log').write_text(p.stdout)
 ok=p.returncode==0 and f'PASS PHYSICAL JTAG {variant}: inputs=128 forecasts=104' in p.stdout
 if ok!=expected:raise SystemExit(f'Mock check failed {variant}/{scenario}:\n'+p.stdout)
 print('MOCK ONLY host test:',variant,scenario,'accepted' if ok else 'correctly rejected',flush=True)
