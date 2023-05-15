"use strict";(self.webpackChunkresearch=self.webpackChunkresearch||[]).push([[7202],{3905:(e,t,r)=>{r.d(t,{Zo:()=>p,kt:()=>f});var i=r(7294);function n(e,t,r){return t in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}function o(e,t){var r=Object.keys(e);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);t&&(i=i.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),r.push.apply(r,i)}return r}function a(e){for(var t=1;t<arguments.length;t++){var r=null!=arguments[t]?arguments[t]:{};t%2?o(Object(r),!0).forEach((function(t){n(e,t,r[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(r)):o(Object(r)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(r,t))}))}return e}function s(e,t){if(null==e)return{};var r,i,n=function(e,t){if(null==e)return{};var r,i,n={},o=Object.keys(e);for(i=0;i<o.length;i++)r=o[i],t.indexOf(r)>=0||(n[r]=e[r]);return n}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(i=0;i<o.length;i++)r=o[i],t.indexOf(r)>=0||Object.prototype.propertyIsEnumerable.call(e,r)&&(n[r]=e[r])}return n}var c=i.createContext({}),l=function(e){var t=i.useContext(c),r=t;return e&&(r="function"==typeof e?e(t):a(a({},t),e)),r},p=function(e){var t=l(e.components);return i.createElement(c.Provider,{value:t},e.children)},u="mdxType",d={inlineCode:"code",wrapper:function(e){var t=e.children;return i.createElement(i.Fragment,{},t)}},h=i.forwardRef((function(e,t){var r=e.components,n=e.mdxType,o=e.originalType,c=e.parentName,p=s(e,["components","mdxType","originalType","parentName"]),u=l(r),h=n,f=u["".concat(c,".").concat(h)]||u[h]||d[h]||o;return r?i.createElement(f,a(a({ref:t},p),{},{components:r})):i.createElement(f,a({ref:t},p))}));function f(e,t){var r=arguments,n=t&&t.mdxType;if("string"==typeof e||n){var o=r.length,a=new Array(o);a[0]=h;var s={};for(var c in t)hasOwnProperty.call(t,c)&&(s[c]=t[c]);s.originalType=e,s[u]="string"==typeof e?e:n,a[1]=s;for(var l=2;l<o;l++)a[l]=r[l];return i.createElement.apply(null,a)}return i.createElement.apply(null,r)}h.displayName="MDXCreateElement"},665:(e,t,r)=>{r.r(t),r.d(t,{assets:()=>c,contentTitle:()=>a,default:()=>d,frontMatter:()=>o,metadata:()=>s,toc:()=>l});var i=r(7462),n=(r(7294),r(3905));const o={title:"Accountable Light Client Systems for Secure and Efficient Bridges"},a=void 0,s={unversionedId:"crypto/LightClientBridgesindex",id:"crypto/LightClientBridgesindex",title:"Accountable Light Client Systems for Secure and Efficient Bridges",description:"Authors: Oana Ciobotaru",source:"@site/docs/crypto/LightClientBridgesindex.md",sourceDirName:"crypto",slug:"/crypto/LightClientBridgesindex",permalink:"/crypto/LightClientBridgesindex",draft:!1,editUrl:"https://github.com/w3f/research/blob/main/docs/docs/crypto/LightClientBridgesindex.md",tags:[],version:"current",frontMatter:{title:"Accountable Light Client Systems for Secure and Efficient Bridges"},sidebar:"sidebar",previous:{title:"Two-Round Trip Schnorr Multi-Signatures via Delinearized Witnesses",permalink:"/crypto/multisig"},next:{title:"Team Members",permalink:"/team_members/"}},c={},l=[],p={toc:l},u="wrapper";function d(e){let{components:t,...r}=e;return(0,n.kt)(u,(0,i.Z)({},p,r,{components:t,mdxType:"MDXLayout"}),(0,n.kt)("p",null,(0,n.kt)("strong",{parentName:"p"},"Authors"),": ",(0,n.kt)("a",{parentName:"p",href:"/team_members/Oana"},"Oana Ciobotaru")),(0,n.kt)("p",null,"A major challenge for blockchain interoperability is having an on-chain light client protocol that is both efficient and secure. We present ",(0,n.kt)("a",{parentName:"p",href:"https://eprint.iacr.org/2022/1205"},"a protocol that provides short proofs about the state of a decentralised consensus")," while being able to detect misbehaving parties. To do this naively, a verifier would need to maintain an updated list of all participants' public keys which makes the corresponding proofs long. In general, existing solutions either lack accountability or are not efficient. We define and design a committee key scheme with short proofs that do not include any of the individual participants' public keys in plain. Our committee key scheme, in turn, uses a custom designed SNARK which has a fast prover time. Moreover, using our committee key scheme, we define and design an accountable light client system as the main cryptographic core for building bridges between proof of stake blockchains. Finally, ",(0,n.kt)("a",{parentName:"p",href:"https://github.com/w3f/apk-proofs"},"we implement a prototype of our custom SNARK")," for which we provide benchmarks. "),(0,n.kt)("p",null,"More concretely, we aim to use the solution described above for building a BLS-based bridge between Kusama and Polkadot. The light client verifier of any such bridge would be ",(0,n.kt)("a",{parentName:"p",href:"https://github.com/paritytech/grandpa-bridge-gadget/blob/master/docs/beefy.md"},"GRANDPA-based")," and, if designed naively, would require verifying hundreds of signatures for every justification. Using aggregation of BLS signatures, we can reduce this to verifying one signature against hundreds of public keys. In our solution linked above, we do not need to communicate either hundreds of public keys or hundreds of signatures."),(0,n.kt)("p",null,"Classical BLS signatures (as described for example in ",(0,n.kt)("a",{parentName:"p",href:"http://toc.cryptobook.us/book.pdf"},"Chapter 15.5, construction 15.5.3.2."),") have fast aggregated signature verification but slow individual signature verification. Since our accountable light client system linked above and, implicitly our bridge design can benefit from BLS signatures with more efficient verification in the individual and aggregated case, ",(0,n.kt)("a",{parentName:"p",href:"https://eprint.iacr.org/2022/1611"},"we propose a three part optimisation that dramatically reduces CPU time in large distributed systems using BLS signatures"),":  First, public keys should be given on both source groups, with a proof-of-possession check for correctness. Second, aggregated BLS signatures should carry their particular aggregate public key in the second source group, so that verifiers can do both hash-to-curve and aggregate public key checks in the first source group. Third, individual non-aggregated BLS signatures should carry short ",(0,n.kt)("a",{parentName:"p",href:"https://link.springer.com/content/pdf/10.1007/3-540-48071-4_7.pdf"},"Chaum-Pedersen DLEQ proofs of correctness"),", so that verifying individual signatures no longer requires pairings, which makes their verification much faster. We prove security for these optimisations. The proposed scheme is implemented and benchmarked to compare with classical BLS scheme."))}d.isMDXComponent=!0}}]);