// 1 Cover
s=newslide('', 'Cover illustration generated for this deck. It is atmospheric artwork, not experimental evidence.', false, true);
await image(s,'docs/presentation/final_defense/assets/weather_cover.png',0,0,1280,720);
text(s,'Weather forecasting\non FPGA',62,122,980,222,100,C.white,true);
text(s,'Parallel inference and verification\non Cyclone II',67,388,650,90,34,'#DBE7E9');
text(s,'CE436',67,624,180,36,24,C.white,true);
text(s,'Final defense',1015,625,200,34,24,C.white,false,'right');
s.speakerNotes.text=notes[1]+'\n\n30 seconds. Scope: weather-speed implementation only, with temperature prototype as development history. The background is a generated weather illustration and does not depict an experiment. Design references: BrightCarbon Siemens metering managed services portfolio, https://www.brightcarbon.com/portfolio/siemens-metering-managed-services-presentation/ .';
// 2 System boundary and forecast time
s=newslide('Three hours ahead','Source: hardware/jtag/README.md; weather_system_speed.v',false,false);
text(s,'3',52,168,290,260,238,C.ink,true);
text(s,'HOURS',70,445,270,58,45,C.ink,true);
line(s,380,182,0,350,C.line,2);
text(s,'12:00',458,184,250,80,64,C.ink,true);
text(s,'Latest observation',458,274,350,45,28,C.gray);
text(s,'15:00',961,184,255,80,64,C.teal,true,'right');
text(s,'Forecast target',901,274,315,45,28,C.gray,false,'right');
arrow(s,762,216,135,C.teal);
text(s,'Recorded frames',458,391,350,45,30,C.ink,true);
text(s,'Host',458,462,170,45,29,C.ink);
arrow(s,613,479,65,C.gray);
text(s,'JTAG',701,462,150,45,29,C.ink);
arrow(s,827,479,65,C.gray);
text(s,'FPGA',923,462,170,45,29,C.ink);
text(s,'Fixed coefficients. Results return to the host.',458,551,755,42,27,C.gray);
text(s,'Temperature    Pressure    Humidity    Wind speed    Direction',67,627,1130,40,26,C.ink);
// 3 Development comparison
s=newslide('The weather extension','Source: original temperature model; weather_v2/models/model.json');
text(s,'1',65,140,200,145,125,C.gray,true);text(s,'quantity in the\ntemperature prototype',252,166,375,100,32,C.gray);
text(s,'5',707,140,150,145,125,C.teal,true);text(s,'weather quantities\nfrom six arithmetic lanes',870,166,355,100,32,C.ink);
line(s,66,320,1148,0,C.line,2);
table(s,[['Design','Temperature prototype','Current weather design'],['Model','Three-parameter seasonal OLS','Seven-lag regression per channel'],['Arithmetic','One lane, 16-bit Q8','Six lanes, 18-bit Q8'],['Direction','No direction path','Cosine and sine with CORDIC']],65,354,1150,225,[185,420,545],25);
text(s,'Hourly inputs and a three-hour target horizon remain the same.',65,615,1150,40,29,C.ink);
// 4 Chronological split
s=newslide('A chronological test','Source: NASA POWER data; weather_v2/software/train_models.py');
text(s,'2021',65,190,200,55,38,C.ink,true);text(s,'2023',630,190,180,55,38,C.ink,true,'right');text(s,'2024',849,190,170,55,38,C.teal,true);text(s,'2025',1066,190,150,55,38,C.amber,true);
rect(s,65,268,715,98,C.ink);rect(s,792,268,205,98,C.teal);rect(s,1009,268,205,98,C.amber);
text(s,'Training',89,290,550,54,36,C.white,true);text(s,'Validation',809,291,172,53,30,C.white,true);text(s,'Test',1031,291,160,53,36,C.white,true);
text(s,'26,253',65,403,620,90,72,C.ink,true);text(s,'8,781',792,403,205,90,52,C.teal,true);text(s,'8,757',1009,403,205,90,52,C.amber,true);
text(s,'usable examples',65,501,600,38,25,C.gray);text(s,'Model selection',792,501,210,38,24,C.gray);text(s,'Held-out period',1009,501,210,38,24,C.gray);
text(s,'NASA POWER hourly observations',65,592,750,42,30,C.ink,true);
text(s,'Ho Chi Minh City, 2021–2025 UTC',65,637,1000,35,25,C.gray);
// 5 Model
s=newslide('Seven lags per channel','Source: weather_v2/models/model.json; seven weights and one bias for each channel',false,true);
text(s,'x̂(t + 3) = bias + Σ wₖ x(t − ℓₖ)',65,190,1150,95,57,C.white,true);
text(s,'Selected lags in hours',65,347,800,40,28,'#A8BCC5');
[0,1,3,6,12,21,24].forEach((l,i)=>{const x=68+i*166;line(s,x+28,420,0,37,l===0?C.teal:'#657C86',3);text(s,String(l),x,474,112,80,62,l===0?C.teal:C.white,true);});
line(s,96,418,996,0,'#657C86',3);
text(s,'Each variable uses its own history.',65,609,1050,43,33,C.white);
// 6 Angle geometry and conversion
s=newslide('Wind direction around 0°','Source: wind_direction_cordic.v; selected direction component models');
shape(s,'ellipse',74,203,350,350,'none',C.line,3);line(s,249,217,0,320,C.line,2);line(s,89,378,320,0,C.line,2);
// A magnified view separates the two nearby directions for visibility.
s.shapes.add({geometry:'line',position:{left:249,top:378,width:170,height:0,rotation:-5},fill:'none',line:{fill:C.teal,width:4,style:'solid'}});
s.shapes.add({geometry:'line',position:{left:249,top:378,width:170,height:0,rotation:5},fill:'none',line:{fill:C.amber,width:4,style:'solid'}});
text(s,'1°',327,286,96,45,32,C.teal,true);text(s,'359°',320,426,115,45,32,C.amber,true);
text(s,'2° apart',105,580,300,55,44,C.ink,true,'center');
text(s,'cos θ',526,208,180,62,43,C.teal,true);text(s,'sin θ',526,300,180,62,43,C.teal,true);
line(s,752,233,0,99,C.line,2);line(s,710,233,42,0,C.line,2);line(s,710,332,42,0,C.line,2);arrow(s,752,278,88,C.ink);
text(s,'CORDIC',872,237,345,62,49,C.ink,true);text(s,'16 iterations',874,310,330,45,31,C.gray);
text(s,'Predicted components become one angle.',526,442,675,90,34,C.ink);
text(s,'Zero vector: direction undefined',526,581,680,44,28,C.gray);
s.speakerNotes.text+='\nThe near-zero rays are separated visually for legibility and are not drawn to angular scale. Their labels are 1° and 359°, whose circular difference is 2°. Host component encoding retains the dataset meteorological convention.';
// 7 Numeric representation
s=newslide('Fixed-point arithmetic','Source: weather_ar_channel.v; weather_reference.cpp');
text(s,'18',57,158,290,215,183,C.ink,true);text(s,'signed bits',65,402,300,57,42,C.ink,true);text(s,'Q8 input and output',65,469,320,45,28,C.gray);
line(s,405,183,0,390,C.line,2);
text(s,'Sample Q8',474,186,300,53,36,C.ink,true);text(s,'×',797,191,70,50,40,C.gray);text(s,'Weight Q14',905,186,310,53,36,C.ink,true);
line(s,475,275,740,0,C.line,2);
text(s,'36-bit product',474,310,740,60,43,C.teal,true);text(s,'Q22',1037,320,175,43,29,C.gray,false,'right');
arrow(s,804,395,100,C.teal);
text(s,'48-bit accumulation',474,457,740,65,43,C.ink,true);
text(s,'Aligned bias, arithmetic shift by 14, range limits',474,543,740,80,28,C.gray);
text(s,'30 °C = 7680 raw',65,613,330,42,29,C.ink,true);
// 8 Parallel architecture
s=newslide('Six parallel arithmetic lanes','Source: weather_predictor_speed.v; weather_ar_channel.v',false,true);
const lanes=['Temperature','Pressure','Humidity','Wind speed','Cosine','Sine'];
lanes.forEach((a,i)=>{const y=184+i*61;text(s,a,65,y,225,42,29,C.white,i<4);line(s,310,y+23,190,0,'#637985',2);shape(s,'ellipse',489,y+14,18,18,C.teal);text(s,'history',535,y,140,42,25,'#ABC1C8');line(s,680,y+23,125,0,'#637985',2);text(s,'×  +',847,y-2,140,45,34,C.teal,true);line(s,983,y+23,215,0,'#637985',2);});
text(s,'One multiplier per lane',65,594,1145,47,37,C.white,true);
text(s,'Each multiplier processes seven lag terms over time.',65,645,1145,34,26,'#ABC1C8');
// 9 Latency
s=newslide('Latency and acceptance interval','Source: weather_system_speed.v; RTL post-edge observation convention',false,true);
text(s,'40',54,150,335,220,186,C.teal,true);text(s,'cycles',67,387,330,67,48,C.white,true);text(s,'0.80 µs at 50 MHz',65,478,340,64,32,'#ABC1C8');
const sx=478,unit=17.9;
text(s,'Frame A',sx,190,700,43,29,C.white,true);
rect(s,sx,253,22*unit,68,C.teal);rect(s,sx+22*unit,253,18*unit,68,C.amber);
text(s,'Arithmetic',sx+18,265,350,43,27,C.ink,true);text(s,'Direction',sx+22*unit+20,265,280,43,27,C.ink,true);
text(s,'N',sx,339,100,40,25,C.white);text(s,'N + 22',sx+22*unit-80,339,150,40,25,C.white);text(s,'N + 40',sx+40*unit-145,339,145,40,25,C.white,false,'right');
text(s,'Frame B',sx,421,700,43,29,C.white,true);
rect(s,sx+23*unit,484,17*unit,60,C.teal);text(s,'Next acceptance',sx+23*unit+15,494,280,40,26,C.ink,true);
text(s,'N + 23',sx+23*unit-45,559,240,40,27,C.white,true);
text(s,'First forecast follows the 25th accepted frame.',65,639,1145,34,26,'#ABC1C8');
// 10 Verification, sequential progression
s=newslide('Verification through deployment','Source: IMPLEMENTATION_REPORT.md; core SDF manifest; physical replay log');
const verify=[['RTL + DPI-C','1,124 forecasts','1,200 accepted frames'],['Core SDF','264 forecasts','288 input frames'],['Physical JTAG','104 forecasts','128 input frames']];
verify.forEach((d,i)=>{const y=185+i*139;line(s,65,y+104,1150,0,C.line,1);text(s,String(i+1).padStart(2,'0'),65,y,90,75,53,C.gray,true);text(s,d[0],190,y+5,370,67,42,C.ink,true);text(s,d[1],645,y+3,570,67,45,i===2?C.teal:C.ink,true,'right');text(s,d[2],645,y+75,570,31,24,C.gray,false,'right');});
text(s,'Values, transaction order, reset behavior and cycle timing',65,632,1145,36,27,C.gray);
s.speakerNotes.text+='\nRTL test: 1124 completed forecasts, four canceled by reset, repeated warm-up. Core SDF uses maximum delays at 20 ns; this is not a whole-JTAG SDF claim. Physical JTAG records actual FPGA responses. Mock host API tests are not physical evidence.';
// 11 Native accuracy charts
s=newslide('Forecast error on the 2025 test set','Source: weather_v2/reports/metrics.csv');
const metrics=[['Temperature','°C',[.507906,2.080369,.832280]],['Pressure','kPa',[.034600,.135167,.085775]],['Humidity','percentage points',[2.614292,8.831186,3.804237]],['Wind speed','m/s',[.566878,.830494,.891217]],['Direction','degrees',[18.084598,21.423810,35.292273]]];
metrics.forEach((d,i)=>{const x=65+i*234;text(s,d[0],x,190,218,43,30,C.ink,true);text(s,d[1],x,239,218,35,22,C.gray);s.charts.add('bar',{position:{left:x-8,top:298,width:223,height:265},categories:['MAE'],series:d[2].map((v,k)=>({name:['Selected','Latest value','Previous day'][k],values:[v],fill:[C.teal,'#8D9DA4','#C4CBCD'][k]})),barOptions:{direction:'column',grouping:'clustered',gapWidth:45},hasLegend:false,dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:21,typeface:BODY,fill:C.ink},numberFormatCode:i===1?'0.000':'0.00'},xAxis:{visible:false},yAxis:{minimumScale:0,visible:false},chartFill:C.light,plotAreaFill:C.light});});
[[C.teal,'Selected model'],['#8D9DA4','Latest value'],['#C4CBCD','Previous day']].forEach(([c,t],i)=>{rect(s,66+i*376,596,19,19,c);text(s,t,99+i*376,584,310,42,25,C.ink);});
text(s,'Lower MAE is better. Each chart uses its own unit and scale.',65,647,1130,31,23,C.gray);
s.speakerNotes.text='Selected models beat both baselines in this chronological test set. Scalar outputs use 8757 examples. Direction uses 8593 targets with wind speed at least 0.5 m/s, ideal atan2 of the quantized component predictions. Hardware CORDIC conversion is checked separately. The maximum measured conversion error in the exhaustive integer-component test is 0.005635 degrees. Full MAE/RMSE values in backup slide B3. Planned time: 55 seconds. Source: versions/weather_v2/reports/metrics.csv.';
// 12 Fit evidence
s=newslide('The fitted Cyclone II implementation','Source: original Quartus Flow Summary; uninstrumented weather-speed JTAG build',false,true);
rect(s,65,172,789,408,C.white);
await shot(s,'weather_speed_flow_summary',65,172,789,408,{left:420/2448,top:105/1378,right:(2448-1550)/2448,bottom:(1378-570)/1378});
text(s,'6,253',900,169,315,98,78,C.teal,true);text(s,'logic elements',905,273,310,45,31,C.white);
line(s,904,343,310,0,'#536A74',2);text(s,'50 MHz',900,379,315,73,54,C.white,true);text(s,'Physical test clock',905,461,310,42,28,'#ABC1C8');
text(s,'7.459 ns setup slack',65,614,720,48,35,C.white,true);text(s,'79.74 MHz estimated Fmax',780,622,435,38,28,'#ABC1C8',false,'right');
s.speakerNotes.text+='\nNative screenshot, no displayed values altered. Twelve 9-bit multiplier elements correspond to six 18-by-18 multipliers. 4571 registers, zero mapped memory bits. Static timing: setup slack 7.459 ns, hold 0.215 ns. Physical tests use 50 MHz, no measured maximum-clock sweep. SignalTap excluded from these fit numbers. Native timing panels in B5.';
// 13 Waveform evidence
s=newslide('A captured physical forecast','Source: native SignalTap weather_speed capture and physical replay log');
await shot(s,'weather_speed_signaltap_detail',45,190,1190,258);
text(s,'104',65,490,245,117,99,C.teal,true);text(s,'forecasts checked\nfrom 128 input frames',333,511,420,86,31,C.ink,true);
line(s,790,499,0,100,C.line,2);text(s,'01A72 hex',848,496,365,49,34,C.ink,true);text(s,'26.4453 °C',848,557,365,50,35,C.ink);
text(s,'41 acquisition intervals correspond to the documented 40-cycle RTL convention.',65,645,1150,32,23,C.gray);
s.speakerNotes.text+='\nOriginal native SignalTap screenshot. The replay log records PASS PHYSICAL JTAG weather_speed: inputs=128 forecasts=104. Temperature raw hexadecimal 01A72 equals decimal 6770, or 26.4453125 degrees C. SignalTap acceptance at index215, forecast_valid at256. Capture sampling sees 41 recorded intervals, while post-edge RTL schedule defines40 cycles. Angle hex00570 equals5.4375 degrees. SignalTap is a separately instrumented build. See native STP and decoded CSV.';
// 14 Scope
s=newslide('Demonstrated scope','Source: retained implementation and physical session records');
text(s,'Recorded observations\nFixed coefficients\nJTAG host readback',65,181,700,227,45,C.ink,true);
text(s,'Five weather quantities on FPGA',65,490,730,60,39,C.teal,true);text(s,'Physical replay at 50 MHz',65,558,730,54,33,C.gray);
rect(s,861,0,419,720,C.ink);text(s,'Further work',901,190,320,60,40,C.white,true);text(s,'Live acquisition\nOther sites and years\nPower measurement',901,301,320,185,30,'#BBCBD0');
text(s,'Rainfall probability lies outside\nthe implemented targets.',901,553,320,85,25,'#BBCBD0');
// 15 Closing
s=newslide('', 'Source: selected models, production RTL, fitted reports and saved physical session', false,true);
await image(s,'docs/presentation/final_defense/assets/weather_cover.png',0,0,1280,720);
text(s,'Weather inference,\nverified on FPGA',65,133,1115,196,83,C.white,true);
text(s,'Five forecast quantities',70,394,1090,49,38,C.white,true);
text(s,'0.80 µs full RTL latency at 50 MHz',70,466,1090,46,32,'#D9E7E8');
text(s,'104 physical forecasts checked',70,525,1090,46,32,'#D9E7E8');
text(s,'Questions',70,639,1090,40,27,C.white);
s.speakerNotes.text=notes[15]+'\nPlanned speaking time:35 seconds. Scope: recorded input replay and fixed coefficients. Latency is documented RTL post-edge latency. The 104 physical forecasts belong to a128-frame test. Cover background repeated as a background, not as evidence.';
