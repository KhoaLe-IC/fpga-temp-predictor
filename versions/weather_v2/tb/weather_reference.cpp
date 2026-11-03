// Independent signed 64-bit FIR reference. No RTL-width slicing before final saturation.
#include <array>
#include <cstdint>
#include <fstream>
#include <stdexcept>
#include <string>
struct Model {
 std::array<std::array<int,25>,6> hist{};
 std::array<std::array<int,7>,6> weights{};
 std::array<int,6> bias{}; int count=0;
 Model(){
  std::ifstream f("reference_coefficients.txt");if(!f)throw std::runtime_error("coefficients missing");
  for(int c=0;c<6;c++){for(auto &v:weights[c])if(!(f>>v))throw std::runtime_error("bad coefficients");if(!(f>>bias[c]))throw std::runtime_error("bad bias");}
 }
};
extern "C" void* weather_create(){try{return new Model;}catch(...){return nullptr;}}
extern "C" void weather_destroy(void*p){delete static_cast<Model*>(p);}
extern "C" void weather_reset(void*p){auto&m=*static_cast<Model*>(p);m.hist={};m.count=0;}
extern "C" int weather_push(void*p,int a,int b,int c,int d,int e,int f,int*oa,int*ob,int*oc,int*od,int*oe,int*of){
 auto&m=*static_cast<Model*>(p);int in[]={a,b,c,d,e,f};int*out[]={oa,ob,oc,od,oe,of};constexpr int lag[]={0,1,3,6,12,21,24};
 for(int ch=0;ch<6;ch++){if(in[ch]<-131072||in[ch]>131071)return -1;for(int i=24;i>0;i--)m.hist[ch][i]=m.hist[ch][i-1];m.hist[ch][0]=in[ch];}
 if(++m.count<25)return 0;
 for(int ch=0;ch<6;ch++){
  int64_t sum=int64_t(m.bias[ch])*16384;for(int k=0;k<7;k++)sum+=int64_t(m.weights[ch][k])*m.hist[ch][lag[k]];
  int64_t value=sum>=0 ? sum/16384 : -((-sum+16383)/16384);
  if(ch==2){if(value<0)value=0;if(value>25600)value=25600;}
  if(ch==3 && value<0)value=0;
  if(ch>=4){if(value<-256)value=-256;if(value>256)value=256;}
  if(value<-131072)value=-131072;if(value>131071)value=131071;*out[ch]=int(value);
 }
 return 1;
}
#ifdef STANDALONE
#include <iostream>
#include <cmath>
int main(){
 try{Model m;int in[6],out[6];
 while(std::cin>>in[0]>>in[1]>>in[2]>>in[3]>>in[4]>>in[5]){
 int valid=weather_push(&m,in[0],in[1],in[2],in[3],in[4],in[5],&out[0],&out[1],&out[2],&out[3],&out[4],&out[5]);
 if(valid<0)return 2;
 for(int v:in)std::cout<<v<<' ';std::cout<<valid;
 for(int c=0;c<6;c++)std::cout<<' '<<(valid?out[c]:0);
 double a=valid?std::atan2(out[5],out[4])*180/3.141592653589793:0;if(a<0)a+=360;
 std::cout<<' '<<int(a*256)<<'\n';
 }return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
#endif
