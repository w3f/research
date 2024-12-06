"use strict";(self.webpackChunkresearch=self.webpackChunkresearch||[]).push([[4107],{5680:(e,t,r)=>{r.d(t,{xA:()=>c,yg:()=>d});var o=r(6540);function n(e,t,r){return t in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}function a(e,t){var r=Object.keys(e);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);t&&(o=o.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),r.push.apply(r,o)}return r}function i(e){for(var t=1;t<arguments.length;t++){var r=null!=arguments[t]?arguments[t]:{};t%2?a(Object(r),!0).forEach((function(t){n(e,t,r[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(r)):a(Object(r)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(r,t))}))}return e}function p(e,t){if(null==e)return{};var r,o,n=function(e,t){if(null==e)return{};var r,o,n={},a=Object.keys(e);for(o=0;o<a.length;o++)r=a[o],t.indexOf(r)>=0||(n[r]=e[r]);return n}(e,t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(o=0;o<a.length;o++)r=a[o],t.indexOf(r)>=0||Object.prototype.propertyIsEnumerable.call(e,r)&&(n[r]=e[r])}return n}var s=o.createContext({}),l=function(e){var t=o.useContext(s),r=t;return e&&(r="function"==typeof e?e(t):i(i({},t),e)),r},c=function(e){var t=l(e.components);return o.createElement(s.Provider,{value:t},e.children)},m="mdxType",u={inlineCode:"code",wrapper:function(e){var t=e.children;return o.createElement(o.Fragment,{},t)}},f=o.forwardRef((function(e,t){var r=e.components,n=e.mdxType,a=e.originalType,s=e.parentName,c=p(e,["components","mdxType","originalType","parentName"]),m=l(r),f=n,d=m["".concat(s,".").concat(f)]||m[f]||u[f]||a;return r?o.createElement(d,i(i({ref:t},c),{},{components:r})):o.createElement(d,i({ref:t},c))}));function d(e,t){var r=arguments,n=t&&t.mdxType;if("string"==typeof e||n){var a=r.length,i=new Array(a);i[0]=f;var p={};for(var s in t)hasOwnProperty.call(t,s)&&(p[s]=t[s]);p.originalType=e,p[m]="string"==typeof e?e:n,i[1]=p;for(var l=2;l<a;l++)i[l]=r[l];return o.createElement.apply(null,i)}return o.createElement.apply(null,r)}f.displayName="MDXCreateElement"},6364:(e,t,r)=>{r.r(t),r.d(t,{assets:()=>s,contentTitle:()=>i,default:()=>u,frontMatter:()=>a,metadata:()=>p,toc:()=>l});var o=r(8168),n=(r(6540),r(5680));const a={title:"A verifiably secure and proportional committee election rule"},i=void 0,p={unversionedId:"Polkadot/protocols/NPoS/Paper",id:"Polkadot/protocols/NPoS/Paper",title:"A verifiably secure and proportional committee election rule",description:"Authors: Alfonso Cevallos and Alistair Stewart",source:"@site/docs/Polkadot/protocols/NPoS/2. Paper.md",sourceDirName:"Polkadot/protocols/NPoS",slug:"/Polkadot/protocols/NPoS/Paper",permalink:"/Polkadot/protocols/NPoS/Paper",draft:!1,editUrl:"https://github.com/w3f/research/blob/master/docs/Polkadot/protocols/NPoS/2. Paper.md",tags:[],version:"current",sidebarPosition:2,frontMatter:{title:"A verifiably secure and proportional committee election rule"},sidebar:"sidebar",previous:{title:"Overview of NPoS",permalink:"/Polkadot/protocols/NPoS/Overview"},next:{title:"Computing a balanced solution",permalink:"/Polkadot/protocols/NPoS/Balancing"}},s={},l=[],c={toc:l},m="wrapper";function u(e){let{components:t,...r}=e;return(0,n.yg)(m,(0,o.A)({},c,r,{components:t,mdxType:"MDXLayout"}),(0,n.yg)("p",null,(0,n.yg)("strong",{parentName:"p"},"Authors"),": ",(0,n.yg)("a",{parentName:"p",href:"/team_members/alfonso.md"},"Alfonso Cevallos")," and ",(0,n.yg)("a",{parentName:"p",href:"/team_members/alistair"},"Alistair Stewart")),(0,n.yg)("p",null,(0,n.yg)("strong",{parentName:"p"},(0,n.yg)("a",{parentName:"strong",href:"https://arxiv.org/abs/2004.12990"},"arXiv link to reseach paper"))),(0,n.yg)("p",null,(0,n.yg)("strong",{parentName:"p"},"Abstract.")," The property of proportional representation in approval-based committee elections, which has appeared in the social choice literature for over a century, is typically understood as avoiding the underrepresentation of minorities. However, we argue that the security of some distributed systems depends on the opposite goal of preventing the overrepresentation of any minority, a goal not previously formalized which leads us to an optimization objective known as ",(0,n.yg)("em",{parentName:"p"},"maximin support"),". We provide a thorough analysis of its approximability, and propose a new efficient election rule inspired in Phragm\xe9n's methods\nthat achieves a) a constant-factor approximation guarantee for the objective, and b) the property of ",(0,n.yg)("em",{parentName:"p"},"proportional justified representation")," (PJR). However, the most striking feature of the new rule is that one can ",(0,n.yg)("em",{parentName:"p"},"verify")," in linear time that the winning committee satisfies the two aforementioned properties, even when the algorithm is executed by an untrusted party who only communicates the output. Finally, we present an efficient post-computation that, when paired with any approximation algorithm for maximin support, returns a new solution that a) preserves the approximation guarantee and b) can be efficiently verified to satisfy PJR."),(0,n.yg)("p",null,"Our work is motivated by an application on blockchains that implement ",(0,n.yg)("em",{parentName:"p"},"Nominated Proof-of-Stake"),", where the community elects a committee of validators to participate in the consensus protocol, and where preventing overrepresentation protects the network against attacks by an adversarial minority. Our election rule gives rise to a validator election protocol with formal guarantees on security and proportionality, in which the ability to efficiently verify these guarantees on the winning committee proves to be key in adapting the protocol to the trustless and resource-limited nature of blockchains.\nWe provide details of such an implementation in the Polkadot network, launched in 2020."))}u.isMDXComponent=!0}}]);