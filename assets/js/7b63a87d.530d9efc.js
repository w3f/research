"use strict";(self.webpackChunkresearch=self.webpackChunkresearch||[]).push([[6342],{3905:(e,t,n)=>{n.d(t,{Zo:()=>u,kt:()=>f});var r=n(7294);function o(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function i(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function a(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?i(Object(n),!0).forEach((function(t){o(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):i(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function s(e,t){if(null==e)return{};var n,r,o=function(e,t){if(null==e)return{};var n,r,o={},i=Object.keys(e);for(r=0;r<i.length;r++)n=i[r],t.indexOf(n)>=0||(o[n]=e[n]);return o}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(r=0;r<i.length;r++)n=i[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(o[n]=e[n])}return o}var c=r.createContext({}),l=function(e){var t=r.useContext(c),n=t;return e&&(n="function"==typeof e?e(t):a(a({},t),e)),n},u=function(e){var t=l(e.components);return r.createElement(c.Provider,{value:t},e.children)},p="mdxType",d={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},m=r.forwardRef((function(e,t){var n=e.components,o=e.mdxType,i=e.originalType,c=e.parentName,u=s(e,["components","mdxType","originalType","parentName"]),p=l(n),m=o,f=p["".concat(c,".").concat(m)]||p[m]||d[m]||i;return n?r.createElement(f,a(a({ref:t},u),{},{components:n})):r.createElement(f,a({ref:t},u))}));function f(e,t){var n=arguments,o=t&&t.mdxType;if("string"==typeof e||o){var i=n.length,a=new Array(i);a[0]=m;var s={};for(var c in t)hasOwnProperty.call(t,c)&&(s[c]=t[c]);s.originalType=e,s[p]="string"==typeof e?e:o,a[1]=s;for(var l=2;l<i;l++)a[l]=n[l];return r.createElement.apply(null,a)}return r.createElement.apply(null,n)}m.displayName="MDXCreateElement"},3035:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>c,contentTitle:()=>a,default:()=>d,frontMatter:()=>i,metadata:()=>s,toc:()=>l});var r=n(7462),o=(n(7294),n(3905));const i={title:"Utility Token Design"},a=void 0,s={unversionedId:"Polkadot/economics/utilitytokendesign",id:"Polkadot/economics/utilitytokendesign",title:"Utility Token Design",description:"Authors: Samuel H\xe4fner",source:"@site/docs/Polkadot/economics/5-utilitytokendesign.md",sourceDirName:"Polkadot/economics",slug:"/Polkadot/economics/utilitytokendesign",permalink:"/Polkadot/economics/utilitytokendesign",draft:!1,editUrl:"https://github.com/w3f/research/blob/main/docs/docs/Polkadot/economics/5-utilitytokendesign.md",tags:[],version:"current",sidebarPosition:5,frontMatter:{title:"Utility Token Design"},sidebar:"sidebar",previous:{title:"Non-monetary incentives for collective members",permalink:"/Polkadot/economics/gamification"},next:{title:"Security",permalink:"/Polkadot/security/"}},c={},l=[],u={toc:l},p="wrapper";function d(e){let{components:t,...n}=e;return(0,o.kt)(p,(0,r.Z)({},u,n,{components:t,mdxType:"MDXLayout"}),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Authors"),": Samuel H\xe4fner"),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Last updated"),": October 13, 2021"),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},"Paper Link:")," ",(0,o.kt)("a",{parentName:"p",href:"http://ssrn.com/abstract=3954773"},"[SSRN]")),(0,o.kt)("p",null,"In this project, I analyze some general design principles of utility tokens that are native to a proof-of-stake blockchain. Utility tokens are cryptographic tokens whose main economic use is to access and consume the respective token issuer\u2019s services. "),(0,o.kt)("p",null,"The services offered by the Polkadot network consist of parachain slots, which come with shared security and means to communicate with other parachains. To obtain one of the slots, the users --- i.e., the teams building on Polkadot --- need to put forth DOTs in recurrent slot auctions.  "),(0,o.kt)("p",null,"For the analysis, I set up a dynamic general equilibrium model of utility tokens that serve as a means to consume services on a two-sided market platform."),(0,o.kt)("p",null,"On the one side of the platform, there are users that derive utility from consuming the services provided by the platform. On the other side, there are validators that provide the required security and receive tokens in return. Validators need to repeatedly sell some of their tokens to cover their costs; users need to repeatedly buy tokens to consume the services. A token market balances token supply and token demand."),(0,o.kt)("p",null,"The main results of the analysis are the following: First, I find that utility token markets are generally efficient because they result in the socially optimal provision of services. Second, I uncover a tension between the dynamics of utility tokens' value, the evolution of the provided services, and the payment details on the users\u2019 side."))}d.isMDXComponent=!0}}]);