(()=>{"use strict";var e,f,a,d,r,t={},c={};function b(e){var f=c[e];if(void 0!==f)return f.exports;var a=c[e]={id:e,loaded:!1,exports:{}};return t[e].call(a.exports,a,a.exports,b),a.loaded=!0,a.exports}b.m=t,b.c=c,e=[],b.O=(f,a,d,r)=>{if(!a){var t=1/0;for(i=0;i<e.length;i++){a=e[i][0],d=e[i][1],r=e[i][2];for(var c=!0,o=0;o<a.length;o++)(!1&r||t>=r)&&Object.keys(b.O).every((e=>b.O[e](a[o])))?a.splice(o--,1):(c=!1,r<t&&(t=r));if(c){e.splice(i--,1);var n=d();void 0!==n&&(f=n)}}return f}r=r||0;for(var i=e.length;i>0&&e[i-1][2]>r;i--)e[i]=e[i-1];e[i]=[a,d,r]},b.n=e=>{var f=e&&e.__esModule?()=>e.default:()=>e;return b.d(f,{a:f}),f},a=Object.getPrototypeOf?e=>Object.getPrototypeOf(e):e=>e.__proto__,b.t=function(e,d){if(1&d&&(e=this(e)),8&d)return e;if("object"==typeof e&&e){if(4&d&&e.__esModule)return e;if(16&d&&"function"==typeof e.then)return e}var r=Object.create(null);b.r(r);var t={};f=f||[null,a({}),a([]),a(a)];for(var c=2&d&&e;"object"==typeof c&&!~f.indexOf(c);c=a(c))Object.getOwnPropertyNames(c).forEach((f=>t[f]=()=>e[f]));return t.default=()=>e,b.d(r,t),r},b.d=(e,f)=>{for(var a in f)b.o(f,a)&&!b.o(e,a)&&Object.defineProperty(e,a,{enumerable:!0,get:f[a]})},b.f={},b.e=e=>Promise.all(Object.keys(b.f).reduce(((f,a)=>(b.f[a](e,f),f)),[])),b.u=e=>"assets/js/"+({53:"935f2afb",161:"4be44ca5",247:"0f64642c",480:"b3c1bff0",559:"cef840d9",569:"432b9073",609:"792944b3",711:"1d765876",833:"dd77e6ad",1080:"b3c3c200",1087:"0fafd334",1126:"49b07f37",1274:"c6e91dd5",1699:"08aee300",1723:"e0f4a888",2288:"cd82644d",2545:"0044dcf8",2706:"fd39ec16",2743:"4c0501a9",2822:"15383a6f",3218:"9bd6e977",3237:"1df93b7f",4131:"b1d6db9e",4172:"48b11638",4184:"e266b312",4633:"eadee0a3",5461:"24cfe004",5758:"2e7f6221",5916:"417d2c1a",6176:"4bff0fe4",6245:"517aa0f2",6293:"d4a7b3c9",6342:"7b63a87d",6427:"fc88f96d",6713:"dec7ffb4",7202:"8fe491a8",7425:"f3019d23",7745:"1352caf8",7774:"1c84c2c0",7805:"eea22109",7869:"f5249d12",7918:"17896441",8047:"fd11ad49",9121:"42b3ad11",9300:"7a5f63e4",9386:"eae161f6",9402:"ddc384b0",9514:"1be78505",9518:"d55f2e5f",9743:"0b076350",9937:"1130142e",9966:"9a918f7b"}[e]||e)+"."+{53:"2cd08ace",161:"64d1de3e",247:"be69169c",480:"c6ed481d",559:"3b5aa85b",569:"cf4b36a7",609:"6ea8d461",711:"e588448e",833:"4f3f60fc",1080:"a271376b",1087:"75dfa1b0",1126:"081bbdf4",1274:"0d03bba2",1699:"120f4c35",1723:"5b383c95",2288:"451ea7ef",2545:"2099ec6b",2706:"64958077",2743:"4fa5e1f1",2822:"cef9f78e",3218:"78509398",3237:"942a2f89",4131:"ab6b496d",4172:"a72d9d2e",4184:"1b7a8eb2",4633:"0648ee80",4972:"bc9c1678",5461:"300787ce",5758:"52c6f285",5916:"eacac28e",6176:"1fae184a",6245:"5cd9d692",6293:"07a0873e",6342:"374c3894",6427:"770e6e0b",6713:"7782ab70",7202:"ff6ed7ae",7425:"33416ec9",7745:"f4ce6c58",7774:"e63bd49f",7805:"49b0dd17",7869:"fa12845c",7918:"0b6c1a66",8047:"3b6065fe",9121:"b6821faf",9300:"ad775d5a",9386:"5fb31a53",9402:"01e13404",9514:"731f1bf1",9518:"2d0d646c",9743:"f05858fd",9937:"d32e4a73",9966:"e621532c"}[e]+".js",b.miniCssF=e=>{},b.g=function(){if("object"==typeof globalThis)return globalThis;try{return this||new Function("return this")()}catch(e){if("object"==typeof window)return window}}(),b.o=(e,f)=>Object.prototype.hasOwnProperty.call(e,f),d={},r="research:",b.l=(e,f,a,t)=>{if(d[e])d[e].push(f);else{var c,o;if(void 0!==a)for(var n=document.getElementsByTagName("script"),i=0;i<n.length;i++){var u=n[i];if(u.getAttribute("src")==e||u.getAttribute("data-webpack")==r+a){c=u;break}}c||(o=!0,(c=document.createElement("script")).charset="utf-8",c.timeout=120,b.nc&&c.setAttribute("nonce",b.nc),c.setAttribute("data-webpack",r+a),c.src=e),d[e]=[f];var l=(f,a)=>{c.onerror=c.onload=null,clearTimeout(s);var r=d[e];if(delete d[e],c.parentNode&&c.parentNode.removeChild(c),r&&r.forEach((e=>e(a))),f)return f(a)},s=setTimeout(l.bind(null,void 0,{type:"timeout",target:c}),12e4);c.onerror=l.bind(null,c.onerror),c.onload=l.bind(null,c.onload),o&&document.head.appendChild(c)}},b.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},b.p="/",b.gca=function(e){return e={17896441:"7918","935f2afb":"53","4be44ca5":"161","0f64642c":"247",b3c1bff0:"480",cef840d9:"559","432b9073":"569","792944b3":"609","1d765876":"711",dd77e6ad:"833",b3c3c200:"1080","0fafd334":"1087","49b07f37":"1126",c6e91dd5:"1274","08aee300":"1699",e0f4a888:"1723",cd82644d:"2288","0044dcf8":"2545",fd39ec16:"2706","4c0501a9":"2743","15383a6f":"2822","9bd6e977":"3218","1df93b7f":"3237",b1d6db9e:"4131","48b11638":"4172",e266b312:"4184",eadee0a3:"4633","24cfe004":"5461","2e7f6221":"5758","417d2c1a":"5916","4bff0fe4":"6176","517aa0f2":"6245",d4a7b3c9:"6293","7b63a87d":"6342",fc88f96d:"6427",dec7ffb4:"6713","8fe491a8":"7202",f3019d23:"7425","1352caf8":"7745","1c84c2c0":"7774",eea22109:"7805",f5249d12:"7869",fd11ad49:"8047","42b3ad11":"9121","7a5f63e4":"9300",eae161f6:"9386",ddc384b0:"9402","1be78505":"9514",d55f2e5f:"9518","0b076350":"9743","1130142e":"9937","9a918f7b":"9966"}[e]||e,b.p+b.u(e)},(()=>{var e={1303:0,532:0};b.f.j=(f,a)=>{var d=b.o(e,f)?e[f]:void 0;if(0!==d)if(d)a.push(d[2]);else if(/^(1303|532)$/.test(f))e[f]=0;else{var r=new Promise(((a,r)=>d=e[f]=[a,r]));a.push(d[2]=r);var t=b.p+b.u(f),c=new Error;b.l(t,(a=>{if(b.o(e,f)&&(0!==(d=e[f])&&(e[f]=void 0),d)){var r=a&&("load"===a.type?"missing":a.type),t=a&&a.target&&a.target.src;c.message="Loading chunk "+f+" failed.\n("+r+": "+t+")",c.name="ChunkLoadError",c.type=r,c.request=t,d[1](c)}}),"chunk-"+f,f)}},b.O.j=f=>0===e[f];var f=(f,a)=>{var d,r,t=a[0],c=a[1],o=a[2],n=0;if(t.some((f=>0!==e[f]))){for(d in c)b.o(c,d)&&(b.m[d]=c[d]);if(o)var i=o(b)}for(f&&f(a);n<t.length;n++)r=t[n],b.o(e,r)&&e[r]&&e[r][0](),e[r]=0;return b.O(i)},a=self.webpackChunkresearch=self.webpackChunkresearch||[];a.forEach(f.bind(null,0)),a.push=f.bind(null,a.push.bind(a))})()})();