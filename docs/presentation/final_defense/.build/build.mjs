import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root='/home/khoale/Documents/University/Semester_5/CE436_Discrete-Time_Signal_Processing/fpga-temp-predictor';
const wd=path.join(root,'docs/presentation/final_defense');
const out=path.join(wd,'.build');
const P=Presentation.create({slideSize:{width:1280,height:720}});
const C={ink:'#152D48',blue:'#146CAB',teal:'#087E83',gray:'#647283',light:'#E9EFF4',line:'#CED8E1',amber:'#BD760A',white:'#FFFFFF'};
const times=[30,45,65,60,55,65,70,60,65,70,55,65,70,45,35];
const baseline=await fs.readFile(path.join(root,'docs/presentation/FINAL_DEFENSE_15_MIN_BASELINE_EN.md'),'utf8');
const parts=baseline.split(/\n### (\d+) /);let notes={};for(let i=1;i<parts.length;i+=2){const n=+parts[i],b=parts[i+1].split('\n### ')[0];notes[n]=[...b.matchAll(/Say: [“"]([\s\S]*?)[”"]\n/g)].map(m=>m[1]).join('\n\n');}
const slides=[];
const {applyPresentationChartFont}=await import('/home/khoale/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations/container_tools/artifact_tool_utils.mjs');
function shape(s,g,x,y,w,h,fill='none',stroke='none',sw=0){return s.shapes.add({geometry:g,position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:sw,style:'solid'}})}
function text(s,str,x,y,w,h,size=28,color=C.ink,bold=false,align='left'){const q=shape(s,'textbox',x,y,w,h);q.text=str;q.text.style={fontSize:size,typeface:'Carlito',color,bold,alignment:align,verticalAlignment:'middle',wrap:'square',autoFit:'none',insets:0};return q;}
function rect(s,x,y,w,h,fill=C.light,stroke='none',sw=0){return shape(s,'rect',x,y,w,h,fill,stroke,sw)}
function line(s,x,y,w,h,color=C.line,sw=2){return shape(s,'line',x,Math.min(y,y+h),w,Math.abs(h),'none',color,sw)}
function arrow(s,x,y,w,color=C.blue){return shape(s,'rightArrow',x,y,w,14,color)}
function box(s,label,x,y,w,h,fill=C.light,size=28){rect(s,x,y,w,h,fill);text(s,label,x+15,y+8,w-30,h-16,size,C.ink,true,'center');}
function newslide(title,source='',backup=false){const s=P.slides.add();slides.push(s);s.background.fill=C.white;const n=slides.length;if(backup)s.hidden=true;text(s,title,54,34,1170,108,40,C.ink,true);text(s,source,54,674,1120,24,15,C.gray);text(s,backup?'B'+(n-15):String(n).padStart(2,'0'),1190,672,40,26,17,C.gray,false,'right');s.speakerNotes.text=(notes[n]||'')+'\n\n'+(n<=15?`Planned speaking time: ${times[n-1]} seconds.\n`:'Backup slide for questions.\n')+'Source: '+source+'\nProject root: '+root;return s;}
async function image(s,file,x,y,w,h,crop=null){const b=await fs.readFile(path.join(root,file));return s.images.add({blob:b,contentType:'image/png',alt:path.basename(file),fit:'contain',position:{left:x,top:y,width:w,height:h},...(crop?{crop}: {})});}
async function shot(s,name,x,y,w,h,crop=null){return image(s,'docs/reports/defense_session/screenshots/'+name+'.png',x,y,w,h,crop)}
function tag(s,str,x,y,w=240){text(s,str,x,y,w,36,22,C.blue,true)}
function table(s,values,x,y,w,h,widths=null,size=24){const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,...(widths?{columnWidths:widths}:{})});for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){const cell=t.getCell(r,c);cell.fill=r===0?C.ink:(r%2?C.white:C.light);cell.text.style={typeface:'Carlito',fontSize:size,color:r===0?C.white:C.ink,bold:r===0,insets:10};}t.borders.assign({fill:C.line,width:1,style:'solid'});return t;}
let s;
// 1
s=newslide('','Template adapted from Michael Alley, The Craft of Scientific Communication');
text(s,'Weather forecasting\non FPGA',54,105,720,190,76,C.ink,true);
text(s,'From a temperature prototype\nto parallel weather inference',58,325,650,100,34,C.gray);
text(s,'CE436   Discrete-Time Signal Processing and Applications',58,590,900,36,24,C.ink);
['T','P','RH','WS','cos','sin'].forEach((a,i)=>{rect(s,900,160+i*58,245,38,i<4?C.light:'#DBEEEE');text(s,a,918,163+i*58,65,32,23,C.ink,true);rect(s,995,171+i*58,112,14,i<4?C.blue:C.teal)});
text(s,'Six arithmetic channels',900,540,300,36,25,C.blue,true);
s.speakerNotes.text=notes[1]+'\n30 seconds. Template: https://www.craftscicom.org/ae_templates.html. Widescreen assertion–evidence template adapted with project-specific typography and diagrams. Title, graphs and diagrams are editable.';
//2
s=newslide('Hourly observations become a forecast\nthree hours ahead','Source: hardware/jtag/README.md; weather_v2/rtl/weather_system_speed.v');
const blocks=[['Recorded\nweather frames',54],['JTAG\nmailbox',355],['History +\nweather core',656],['Host reads\nthe forecast',957]];
blocks.forEach(([a,x],i)=>{box(s,a,x,285,265,130);if(i<3)arrow(s,x+274,342,20)});
tag(s,'Hourly data',54,225);tag(s,'50 MHz FPGA',656,225);
text(s,'At noon: use known history to predict 15:00',54,485,1120,54,36,C.blue,true);
text(s,'Offline training supplies fixed coefficients.',54,565,1100,42,28,C.gray);
//3
s=newslide('The temperature prototype became\na six-channel weather predictor','Source: software/models_cpp/model.json; versions/weather_v2/models/model.json');
table(s,[['Design choice','Temperature prototype','Current weather design'],['Reported quantities','Temperature','Temperature, pressure, humidity,\nwind speed and direction'],['Model','Three-parameter OLS','Seven-lag regression per channel'],['Datapath','One channel, 16-bit Q8','Six channels, 18-bit Q8'],['Direction output','—','Cosine + sine, then CORDIC']],54,170,1170,390,[265,385,520],26);
text(s,'Retained: hourly observations, a three-hour horizon, 25-frame history.',54,588,1170,52,29,C.blue,true);
//4
s=newslide('Training, model selection and testing\nuse separate time periods','Source: weather_v2/software/train_models.py; models/model.json');
const years=[['2021–2023','Training','26,253',C.ink],['2024','Validation','8,781',C.blue],['2025','Test','8,757',C.teal]];
years.forEach((d,i)=>{let x=54+i*398;rect(s,x,220,370,12,d[3]);text(s,d[0],x,258,370,58,44,d[3],true);text(s,d[1],x,335,370,44,32);text(s,d[2],x,400,370,70,58,d[3],true);text(s,'usable examples',x,480,370,38,24,C.gray)});
text(s,'NASA POWER   Ho Chi Minh City   Hourly observations in UTC',54,580,1160,45,29,C.ink);
//5
s=newslide('Each channel learns from seven past values\nof the same variable','Source: weather_v2/models/model.json; temperature and humidity select ridge penalty 1');
text(s,'x̂(t + 3) = bias + Σ wₖ x(t − ℓₖ)',72,200,1136,80,53,C.blue,true,'center');
const lag=[0,1,3,6,12,21,24];lag.forEach((l,i)=>{let x=64+i*169;box(s,String(l),x,365,145,85,l===0?'#D9EAF5':C.light,44);text(s,l===0?'latest':'hours ago',x,470,145,34,24,C.gray,false,'center')});
text(s,'Seven weights and one bias per channel',64,568,1110,50,34,C.ink,true);
//6
s=newslide('Cosine and sine keep nearby wind directions\nclose across the zero-degree boundary','Source: weather_v2/rtl/wind_direction_cordic.v; model.json');
shape(s,'ellipse',80,210,330,330,'none',C.line,4);line(s,245,225,0,300,C.line,2);line(s,95,375,300,0,C.line,2);s.shapes.add({geometry:'line',position:{left:245,top:370,width:155,height:0,rotation:-3.33},fill:'none',line:{fill:C.blue,width:5,style:'solid'}});s.shapes.add({geometry:'line',position:{left:245,top:380,width:155,height:0,rotation:3.33},fill:'none',line:{fill:C.teal,width:5,style:'solid'}});
text(s,'1°',322,300,100,42,28,C.blue,true);text(s,'359°',325,402,80,40,28,C.teal,true);text(s,'2° apart',130,565,260,46,36,C.ink,true,'center');
box(s,'cos θ',510,235,210,78);box(s,'sin θ',510,380,210,78);arrow(s,735,335,55);box(s,'16-step\nCORDIC',820,285,230,125,'#DBEEEE',32);arrow(s,1065,338,45);text(s,'θ̂',1130,306,90,65,56,C.teal,true);text(s,'Zero predicted vector: direction undefined',510,525,680,55,28,C.gray);
//7
s=newslide('Fixed-point rules make the reference\nand RTL calculations comparable','Source: weather_v2/rtl/weather_ar_channel.v; C++ reference; worked example in report');
const stages=[['18-bit sample\nQ8',54],['18-bit weight\nQ14',350],['36-bit product\nQ22',646],['48-bit\naccumulator',942]];
stages.forEach(([a,x],i)=>{box(s,a,x,215,265,115);if(i===0)text(s,'×',x+270,247,28,45,32,C.blue,true,'center');else if(i===1)text(s,'=',x+270,247,28,45,32,C.blue,true,'center');else if(i===2)arrow(s,x+270,263,20)});
text(s,'Aligned bias',930,355,280,40,28,C.gray);text(s,'Arithmetic shift by 14, then saturation and range limits',54,430,1165,55,34,C.blue,true);
text(s,'30 °C = raw 7680',54,540,515,55,36,C.ink,true);text(s,'Teaching example: raw 8059 = 31.4805 °C',605,540,620,55,29,C.ink);
//8
s=newslide('Six lanes run in parallel, with one multiplier\nreused across each lane’s seven terms','Source: weather_v2/rtl/weather_predictor_speed.v; weather_ar_channel.v');
['Temperature','Pressure','Humidity','Wind speed','Cosine','Sine'].forEach((a,i)=>{const y=177+i*69;text(s,a,54,y,210,45,28,C.ink,true);box(s,'25-frame history',275,y,240,45,C.light,23);arrow(s,525,y+17,35);box(s,'Select lag',570,y,165,45,C.light,23);arrow(s,745,y+17,35);box(s,'Multiply + accumulate',790,y,330,45,i<4?C.light:'#DBEEEE',23)});
text(s,'42 products per frame, distributed over time',54,615,1100,40,28,C.blue,true);
//9
s=newslide('The full forecast takes 40 cycles,\nwith a new eligible frame every 23 cycles','Source: weather_system_speed.v; tb_weather.sv; RTL post-edge observation convention');
const x0=210,scale=21;line(s,x0,250,840,0,C.line,3);[0,22,23,40].forEach((v)=>{line(s,x0+v*scale,237,0,26,C.ink,2);text(s,'N'+(v?' + '+v:''),x0+v*scale-60,v===23?260:178,120,v===23?30:42,v===23?21:25,C.ink,true,'center')});
text(s,'Frame A',54,300,140,45,28,C.ink,true);rect(s,x0,300,22*scale,55,C.blue);rect(s,x0+22*scale,300,18*scale,55,C.teal);text(s,'Seven-term arithmetic',x0+18,308,410,40,24,C.white,true);text(s,'Direction + alignment',x0+22*scale+15,308,350,40,24,C.white,true);
text(s,'Frame B',54,400,140,45,28,C.ink,true);rect(s,x0+23*scale,400,17*scale,55,C.blue);text(s,'Next frame starts',x0+23*scale+12,408,340,40,24,C.white,true);
text(s,'40 × 20 ns = 0.80 µs',54,535,660,70,49,C.blue,true);text(s,'First forecast: accepted frame 25\nJTAG replay has additional host overhead',765,535,460,83,26,C.gray);
//10
s=newslide('Verification checks values, transaction order\nand timing through implementation','Source: IMPLEMENTATION_REPORT.md; weather_speed_modelsim_timing.json');
const ver=[['RTL + DPI-C','1,124','forecasts checked','1,200 accepted frames'],['Core SDF','264','forecasts checked','288 input frames'],['Physical JTAG','104','forecasts checked','128 input frames']];
ver.forEach((d,i)=>{let x=54+i*398;text(s,d[0],x,190,370,50,33,C.ink,true);line(s,x,258,345,0,C.line,2);text(s,d[1],x,292,370,100,78,i===2?C.teal:C.blue,true);text(s,d[2],x,405,370,45,28);text(s,d[3],x,465,370,40,25,C.gray)});
text(s,'Reset cancellation and repeated history warm-up explain the RTL counts.',54,585,1170,50,28,C.gray);
//11 native small-multiple charts
s=newslide('The selected models beat both simple\nbaselines on the chronological test set','Source: weather_v2/reports/metrics.csv; held-out test period: 2025');
const metrics=[['Temperature','°C',[.507906,2.080369,.832280]],['Pressure','kPa',[.034600,.135167,.085775]],['Humidity','percentage points',[2.614292,8.831186,3.804237]],['Wind speed','m/s',[.566878,.830494,.891217]],['Direction','degrees',[18.084598,21.423810,35.292273]]];
metrics.forEach((d,i)=>{let x=54+i*237;text(s,d[0],x,178,220,40,29,C.ink,true);text(s,d[1],x,222,220,35,21,C.gray);let chart=s.charts.add('bar',{position:{left:x,top:277,width:218,height:265},categories:['MAE'],series:d[2].map((v,k)=>({name:['Selected','Latest','Yesterday'][k],values:[v],fill:[C.blue,'#9AAAB8','#D0D9E0'][k]})),barOptions:{direction:'column',grouping:'clustered',gapWidth:45},hasLegend:false,dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:18,typeface:'Carlito',fill:C.ink},numberFormatCode:i===1?'0.000':'0.00'},xAxis:{visible:false},yAxis:{minimumScale:0,visible:false},chartFill:C.white,plotAreaFill:C.white});});
[[C.blue,'Selected model'],['#9AAAB8','Latest-value baseline'],['#D0D9E0','Previous-day baseline']].forEach(([c,t],i)=>{rect(s,54+i*390,570,20,20,c);text(s,t,87+i*390,560,350,40,25,C.ink)});
text(s,'Lower MAE is better. Direction: non-calm targets, ideal angle decoding of quantized components.',54,626,1170,31,20,C.gray);
//12
s=newslide('The fitted weather-speed JTAG build\nmeets the 50 MHz timing constraint','Source: native Quartus screenshots; JTAG_IMPLEMENTATION_REPORT.md; uninstrumented build');
await shot(s,'weather_speed_flow_summary',54,176,706,388,{left:420/2448,top:105/1378,right:(2448-1550)/2448,bottom:(1378-570)/1378});
text(s,'6,253',830,192,370,75,61,C.blue,true);text(s,'logic elements',830,273,370,40,29,C.ink);
text(s,'7.459 ns',830,347,370,65,48,C.teal,true);text(s,'positive setup slack',830,420,370,42,28,C.ink);
text(s,'79.74 MHz',830,496,370,60,43,C.ink,true);text(s,'estimated Fmax',830,563,370,40,26,C.gray);
text(s,'4,571 registers     12 nine-bit multiplier elements     SignalTap excluded',54,605,1160,40,25,C.gray);
//13
s=newslide('Physical replay checked 104 forecasts\nand SignalTap captured a valid transaction','Source: weather_speed_physical_replay.txt; weather_speed.stp; decoded capture CSV');
await shot(s,'weather_speed_signaltap_detail',54,170,1170,254);
rect(s,54,455,1170,64,C.ink);text(s,'PASS PHYSICAL JTAG weather_speed: inputs=128 forecasts=104',75,468,1130,38,28,C.white,true);
text(s,'01A72 hex = 6770 raw = 26.4453 °C',54,548,1160,44,32,C.blue,true);
text(s,'41 capture intervals; 40-cycle RTL latency under the post-edge convention.',54,614,1160,40,24,C.gray);
//14
s=newslide('The demonstrated system uses recorded data\nand fixed coefficients','Source: implementation scope and retained physical evidence, October 2026');
text(s,'Demonstrated',54,183,530,60,40,C.blue,true);text(s,'Recorded inputs over JTAG\nFive forecast quantities\n50 MHz physical replay',54,280,590,230,35,C.ink);
line(s,670,185,0,390,C.line,2);text(s,'Next evaluation',735,183,490,60,40,C.gray,true);text(s,'Live data acquisition\nOther locations and years\nMeasured electrical power',735,280,490,230,35,C.gray);
text(s,'Rainfall probability remains outside the implemented targets.',54,590,1150,50,30,C.ink,true);
//15
s=newslide('A temperature prototype became\nverified weather forecasting hardware','Source: selected model, RTL timing checks, and saved physical replay');
[['5','weather quantities'],['0.80 µs','full RTL latency at 50 MHz'],['104','forecasts checked on FPGA']].forEach((d,i)=>{let y=185+i*147;text(s,d[0],54,y,410,104,i===1?63:78,i===2?C.teal:C.blue,true);text(s,d[1],500,y+20,680,60,35,C.ink,true);if(i<2)line(s,54,y+126,1165,0,C.line,1)});
//16 backup original OLS
s=newslide('The original temperature model used\na seasonal anchor and two corrections','Source: software/models_cpp/model.json; temperature_metrics.csv',true);
text(s,'T̂(t + 3) = T(t − 21) + a Δdaily + b Δrecent + c',54,205,1170,90,40,C.blue,true);
text(s,'Δdaily = T(t) − T(t − 24)\nΔrecent = T(t) − T(t − 3)',54,330,640,135,34);
table(s,[['Parameter','Fitted value'],['a','0.7454870439'],['b','0.0091494450'],['c','0.0011295817 °C']],765,326,460,240,[130,330],24);
text(s,'Temperature test MAE: 0.538017 °C in the prototype; 0.507906 °C in the current model.',54,588,1170,54,29,C.ink,true);
//17 backup numeric
s=newslide('The current temperature lane uses\nseven deployed weights and a Q8 bias','Source: weather_v2/models/model.json; fixed-point teaching calculation in companion',true);
table(s,[['Lag (h)','Input Q8','Weight Q14','Product'],['0','7680','20035','153868800'],['1','7552','−9335','−70497920'],['3','7168','1621','11619328'],['6','6912','−205','−1416960'],['12','6656','15','99840'],['21','7936','13908','110373888'],['24','7424','−10382','−77075968']],54,163,1170,400,[200,260,260,450],24);
text(s,'S = 132050048 including aligned bias.  floor(S / 16384) = 8059.',54,595,1170,46,29,C.blue,true);
//18 backup metrics
s=newslide('Test errors retain the physical unit\nof each forecast quantity','Source: weather_v2/reports/metrics.csv; selected_fixed; test split',true);
table(s,[['Target','MAE','RMSE'],['Temperature (°C)','0.507906','0.730939'],['Pressure (kPa)','0.034600','0.044638'],['Humidity (percentage points)','2.614292','3.685767'],['Wind speed (m/s)','0.566878','0.750218'],['Direction (degrees)','18.084598','30.201056']],54,171,1170,365,[590,290,290],27);
text(s,'8,757 scalar targets. Direction: 8,593 targets with wind speed ≥ 0.5 m/s.',54,565,1170,40,25,C.gray);
text(s,'Direction uses ideal atan2 of quantized components. CORDIC maximum conversion error: 0.005635°.',54,613,1170,40,23,C.gray);
//19 backup full lane schedule
s=newslide('Each lane repeats operand, product\nand accumulation for seven terms','Source: weather_ar_channel.v; tb_weather.sv',true);
table(s,[['Edge','Operation'],['N','Accept frame, shift history, initialize bias'],['N + 1','Capture lag 0 operand'],['N + 2','Capture product'],['N + 3','Add product to accumulator'],['N + 4 … N + 21','Repeat for remaining six terms'],['N + 22','Scale, limit and publish lane result'],['N + 23','Earliest next eligible acceptance']],54,165,1170,420,[240,930],25);
text(s,'Synchronous active-low reset cancels pending work and restarts history eligibility.',54,612,1170,40,25,C.gray);
//20 backup timing native
s=newslide('Native TimeQuest panels record\nthe fitted timing margins','Source: weather_speed_timing_summary.png and weather_speed_fmax.png',true);
await shot(s,'weather_speed_timing_summary',54,170,1170,280,{left:420/2448,top:100/1378,right:(2448-1550)/2448,bottom:(1378-365)/1378});
await shot(s,'weather_speed_fmax',54,478,700,115,{left:420/2448,top:100/1378,right:(2448-1150)/2448,bottom:(1378-210)/1378});
text(s,'Physical test clock: 50 MHz\nFitted estimate: 79.74 MHz',810,478,415,115,29,C.ink,true);
//21 backup nativefull
s=newslide('The original SignalTap acquisition\nretains the decoded buses and trigger','Source: docs/reports/defense_session/signaltap/weather_speed.stp',true);
await shot(s,'weather_speed_signaltap_waveform',54,165,1170,470);
//22 mailbox
s=newslide('The JTAG mailbox holds each request\nand retains the completed forecast','Source: hardware/jtag/README.md; hardware/jtag/jtag_mailbox.v',true);
['Stage payload','Toggle request','Wait for acknowledgement','Read stable result'].forEach((v,i)=>{const x=54+i*300;box(s,v,x,270,270,112,C.light,29);if(i<3)arrow(s,x+275,320,20)});
text(s,'128-bit source word\n256-bit probe word',54,460,560,118,35,C.blue,true);text(s,'One outstanding request\nWarm-up replies acknowledge without a forecast',650,460,575,118,29,C.ink);
//23 provenance
s=newslide('Source records support the model,\nimplementation and physical results','Template and design references; project evidence available in the repository',true);
text(s,'Model and evaluation',54,177,380,45,30,C.blue,true);text(s,'versions/weather_v2/models/model.json\nversions/weather_v2/reports/metrics.csv',460,177,765,86,25);
text(s,'Implementation',54,298,380,45,30,C.blue,true);text(s,'docs/reports/JTAG_IMPLEMENTATION_REPORT.md\ndocs/reports/weather_speed_modelsim_timing.json',460,298,765,86,25);
text(s,'Physical session',54,419,380,45,30,C.blue,true);text(s,'docs/reports/defense_session/\nNative screenshots, replay logs, STP and decoded CSV',460,419,765,86,25);
text(s,'Template adapted from Michael Alley’s 16:9 assertion–evidence template.\nwww.craftscicom.org/ae_templates.html',54,565,1170,75,25,C.gray);
s.speakerNotes.text='Template reference downloaded from https://www.craftscicom.org/uploads/5/6/1/4/56145985/ae_presentation_template_16_9_ratio.pptx and adapted for this engineering defense. Body headline plus visual evidence follows its structure. Typography uses Carlito, the installed Calibri-compatible font. Palette and project diagrams are original adaptations. Additional guidance: https://mitcommlab.mit.edu/broad/commkit/slideshow/ .';
await fs.mkdir(path.join(out,'renders'),{recursive:true});
slides[10].speakerNotes.text='Lower mean absolute error is better. Persistence repeats the latest observation. The diurnal baseline repeats yesterday at the target hour. The selected models beat both on this 2025 test set. Each chart has its own unit and scale. Scalars use 8757 targets. Direction uses 8593 targets with wind speed at least 0.5 m/s and ideal atan2 of quantized components. CORDIC conversion is checked separately. Source: versions/weather_v2/reports/metrics.csv. Planned time: 55 seconds.';
for(const sl of slides)for(const ch of sl.charts.items)applyPresentationChartFont(ch,{fontFamily:'Carlito'});
for(let i=0;i<slides.length;i++){const b=await P.export({slide:slides[i],format:'png',scale:1.25});await fs.writeFile(path.join(out,'renders',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));}
await (await PresentationFile.exportPptx(P)).save(path.join(out,'candidate.pptx'));
await fs.writeFile(path.join(out,'deck.inspect.ndjson'),(await P.inspect({kind:'slide,textbox,chart,table,notes',maxChars:1000000})).ndjson);
console.log('BUILT',slides.length,'slides');
