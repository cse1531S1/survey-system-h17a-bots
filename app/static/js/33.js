webpackJsonp([33],{EtzU:function(t,e,a){e=t.exports=a("FZ+f")(!1),e.push([t.i,".v-avatar{display:inline-block;text-align:center;vertical-align:middle;width:40px;height:40px;border-radius:10px;overflow:hidden;font:300 normal 24px/48px sans-serif}.v-avatar .v-avatar-text{display:inline-block;width:100%;height:100%;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none}",""])},JqIm:function(t,e,a){"use strict";function n(t){a("UTzK")}Object.defineProperty(e,"__esModule",{value:!0});var s=a("aLVE"),i=a("sYjt"),r=a("VU/8"),l=n,o=r(s.a,i.a,l,null,null);e.default=o.exports},UTzK:function(t,e,a){var n=a("EtzU");"string"==typeof n&&(n=[[t.i,n,""]]),n.locals&&(t.exports=n.locals);a("rjj0")("e3773192",n,!0)},aLVE:function(t,e,a){"use strict";var n=a("qVHI"),s=a.n(n);e.a={props:["alt","size"],data:function(){return{}},computed:{bg:function(){return this.alt?s()(this.alt):"black"},fg:function(){if(!this.alt)return"black";var t=s.a.rgb(this.alt);return 299*t[0]+587*t[1]+144*t[2]>2e5?"black":"white"},name:function(){return this.alt?this.alt.charAt(0).toUpperCase():""},styleSize:function(){if(this.size){var t=this.size+"px";return{weith:t,height:t,"line-height":t,"font-size":this.size/2+"px"}}}}}},sYjt:function(t,e,a){"use strict";var n=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("span",{staticClass:"v-avatar",style:t.styleSize,attrs:{"aria-label":t.alt}},[a("span",{staticClass:"v-avatar-text",style:{background:t.bg,color:t.fg},domProps:{textContent:t._s(t.name)}})])},s=[],i={render:n,staticRenderFns:s};e.a=i}});