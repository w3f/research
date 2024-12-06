"use strict";(self.webpackChunkresearch=self.webpackChunkresearch||[]).push([[4360],{5680:(e,t,r)=>{r.d(t,{xA:()=>p,yg:()=>f});var n=r(6540);function c(e,t,r){return t in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}function o(e,t){var r=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),r.push.apply(r,n)}return r}function i(e){for(var t=1;t<arguments.length;t++){var r=null!=arguments[t]?arguments[t]:{};t%2?o(Object(r),!0).forEach((function(t){c(e,t,r[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(r)):o(Object(r)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(r,t))}))}return e}function a(e,t){if(null==e)return{};var r,n,c=function(e,t){if(null==e)return{};var r,n,c={},o=Object.keys(e);for(n=0;n<o.length;n++)r=o[n],t.indexOf(r)>=0||(c[r]=e[r]);return c}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(n=0;n<o.length;n++)r=o[n],t.indexOf(r)>=0||Object.prototype.propertyIsEnumerable.call(e,r)&&(c[r]=e[r])}return c}var s=n.createContext({}),l=function(e){var t=n.useContext(s),r=t;return e&&(r="function"==typeof e?e(t):i(i({},t),e)),r},p=function(e){var t=l(e.components);return n.createElement(s.Provider,{value:t},e.children)},u="mdxType",m={inlineCode:"code",wrapper:function(e){var t=e.children;return n.createElement(n.Fragment,{},t)}},d=n.forwardRef((function(e,t){var r=e.components,c=e.mdxType,o=e.originalType,s=e.parentName,p=a(e,["components","mdxType","originalType","parentName"]),u=l(r),d=c,f=u["".concat(s,".").concat(d)]||u[d]||m[d]||o;return r?n.createElement(f,i(i({ref:t},p),{},{components:r})):n.createElement(f,i({ref:t},p))}));function f(e,t){var r=arguments,c=t&&t.mdxType;if("string"==typeof e||c){var o=r.length,i=new Array(o);i[0]=d;var a={};for(var s in t)hasOwnProperty.call(t,s)&&(a[s]=t[s]);a.originalType=e,a[u]="string"==typeof e?e:c,i[1]=a;for(var l=2;l<o;l++)i[l]=r[l];return n.createElement.apply(null,i)}return n.createElement.apply(null,r)}d.displayName="MDXCreateElement"},3514:(e,t,r)=>{r.d(t,{A:()=>g});var n=r(6540),c=r(53),o=r(1754),i=r(5489),a=r(6654),s=r(1312);const l={cardContainer:"cardContainer_fWXF",cardTitle:"cardTitle_rnsV",cardDescription:"cardDescription_PWke"};function p(e){let{href:t,children:r}=e;return n.createElement(i.A,{href:t,className:(0,c.A)("card padding--lg",l.cardContainer)},r)}function u(e){let{href:t,icon:r,title:o,description:i}=e;return n.createElement(p,{href:t},n.createElement("h2",{className:(0,c.A)("text--truncate",l.cardTitle),title:o},r," ",o),i&&n.createElement("p",{className:(0,c.A)("text--truncate",l.cardDescription),title:i},i))}function m(e){let{item:t}=e;const r=(0,o._o)(t);return r?n.createElement(u,{href:r,icon:"\ud83d\uddc3\ufe0f",title:t.label,description:t.description??(0,s.T)({message:"{count} items",id:"theme.docs.DocCard.categoryDescription",description:"The default description for a category card in the generated index about how many items this category includes"},{count:t.items.length})}):null}function d(e){let{item:t}=e;const r=(0,a.A)(t.href)?"\ud83d\udcc4\ufe0f":"\ud83d\udd17",c=(0,o.cC)(t.docId??void 0);return n.createElement(u,{href:t.href,icon:r,title:t.label,description:t.description??c?.description})}function f(e){let{item:t}=e;switch(t.type){case"link":return n.createElement(d,{item:t});case"category":return n.createElement(m,{item:t});default:throw new Error(`unknown item type ${JSON.stringify(t)}`)}}function y(e){let{className:t}=e;const r=(0,o.$S)();return n.createElement(g,{items:r.items,className:t})}function g(e){const{items:t,className:r}=e;if(!t)return n.createElement(y,e);const i=(0,o.d1)(t);return n.createElement("section",{className:(0,c.A)("row",r)},i.map(((e,t)=>n.createElement("article",{key:t,className:"col col--6 margin-bottom--lg"},n.createElement(f,{item:e})))))}},9330:(e,t,r)=>{r.r(t),r.d(t,{assets:()=>l,contentTitle:()=>a,default:()=>d,frontMatter:()=>i,metadata:()=>s,toc:()=>p});var n=r(8168),c=(r(6540),r(5680)),o=r(3514);const i={title:"Cryptography"},a=void 0,s={unversionedId:"crypto/index",id:"crypto/index",title:"Cryptography",description:"As part of our work, we sometimes pick up general cryptographic topics for research. Here are our current projects:",source:"@site/docs/crypto/index.md",sourceDirName:"crypto",slug:"/crypto/",permalink:"/crypto/",draft:!1,editUrl:"https://github.com/w3f/research/blob/master/docs/crypto/index.md",tags:[],version:"current",frontMatter:{title:"Cryptography"},sidebar:"sidebar",previous:{title:"Slashing across eras with NPoS",permalink:"/Polkadot/security/slashing/npos"},next:{title:"Two-Round Trip Schnorr Multi-Signatures via Delinearized Witnesses",permalink:"/crypto/multisig"}},l={},p=[],u={toc:p},m="wrapper";function d(e){let{components:t,...r}=e;return(0,c.yg)(m,(0,n.A)({},u,r,{components:t,mdxType:"MDXLayout"}),(0,c.yg)("p",null,"As part of our work, we sometimes pick up general cryptographic topics for research. Here are our current projects:"),(0,c.yg)(o.A,{mdxType:"DocCardList"}))}d.isMDXComponent=!0}}]);