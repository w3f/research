"use strict";(self.webpackChunkresearch=self.webpackChunkresearch||[]).push([[6713],{3905:(e,t,r)=>{r.d(t,{Zo:()=>u,kt:()=>f});var s=r(7294);function i(e,t,r){return t in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}function o(e,t){var r=Object.keys(e);if(Object.getOwnPropertySymbols){var s=Object.getOwnPropertySymbols(e);t&&(s=s.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),r.push.apply(r,s)}return r}function n(e){for(var t=1;t<arguments.length;t++){var r=null!=arguments[t]?arguments[t]:{};t%2?o(Object(r),!0).forEach((function(t){i(e,t,r[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(r)):o(Object(r)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(r,t))}))}return e}function a(e,t){if(null==e)return{};var r,s,i=function(e,t){if(null==e)return{};var r,s,i={},o=Object.keys(e);for(s=0;s<o.length;s++)r=o[s],t.indexOf(r)>=0||(i[r]=e[r]);return i}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(s=0;s<o.length;s++)r=o[s],t.indexOf(r)>=0||Object.prototype.propertyIsEnumerable.call(e,r)&&(i[r]=e[r])}return i}var l=s.createContext({}),c=function(e){var t=s.useContext(l),r=t;return e&&(r="function"==typeof e?e(t):n(n({},t),e)),r},u=function(e){var t=c(e.components);return s.createElement(l.Provider,{value:t},e.children)},p="mdxType",h={inlineCode:"code",wrapper:function(e){var t=e.children;return s.createElement(s.Fragment,{},t)}},y=s.forwardRef((function(e,t){var r=e.components,i=e.mdxType,o=e.originalType,l=e.parentName,u=a(e,["components","mdxType","originalType","parentName"]),p=c(r),y=i,f=p["".concat(l,".").concat(y)]||p[y]||h[y]||o;return r?s.createElement(f,n(n({ref:t},u),{},{components:r})):s.createElement(f,n({ref:t},u))}));function f(e,t){var r=arguments,i=t&&t.mdxType;if("string"==typeof e||i){var o=r.length,n=new Array(o);n[0]=y;var a={};for(var l in t)hasOwnProperty.call(t,l)&&(a[l]=t[l]);a.originalType=e,a[p]="string"==typeof e?e:i,n[1]=a;for(var c=2;c<o;c++)n[c]=r[c];return s.createElement.apply(null,n)}return s.createElement.apply(null,r)}y.displayName="MDXCreateElement"},6081:(e,t,r)=>{r.r(t),r.d(t,{assets:()=>l,contentTitle:()=>n,default:()=>h,frontMatter:()=>o,metadata:()=>a,toc:()=>c});var s=r(7462),i=(r(7294),r(3905));const o={title:"Session keys"},n=void 0,a={unversionedId:"Polkadot/security/keys/session",id:"Polkadot/security/keys/session",title:"Session keys",description:"A session public key should consist of three or four public keys types:",source:"@site/docs/Polkadot/security/keys/3-session.md",sourceDirName:"Polkadot/security/keys",slug:"/Polkadot/security/keys/session",permalink:"/Polkadot/security/keys/session",draft:!1,editUrl:"https://github.com/w3f/research/blob/master/docs/Polkadot/security/keys/3-session.md",tags:[],version:"current",sidebarPosition:3,frontMatter:{title:"Session keys"},sidebar:"sidebar",previous:{title:"Nomination",permalink:"/Polkadot/security/keys/staking"},next:{title:"Account key creation ideas for Polkadot",permalink:"/Polkadot/security/keys/creation"}},l={},c=[],u={toc:c},p="wrapper";function h(e){let{components:t,...r}=e;return(0,i.kt)(p,(0,s.Z)({},u,r,{components:t,mdxType:"MDXLayout"}),(0,i.kt)("p",null,"A session public key should consist of three or four public keys types: "),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("p",{parentName:"li"},"Ristretto Schnorr public key (32 bytes public keys, 64 byte signatures, 96 byte VRFs)"),(0,i.kt)("p",{parentName:"li"},"We issue these from the nominator keys acting as validator operators.  We might use an implicit certificate but doing so either restricts us to one validator operator, or else increases code complexity and forces a primary validator operator.  Implicit certificates also make session key records impossible to authenticate without the nominator account, but this sounds desirable.  "),(0,i.kt)("p",{parentName:"li"},'We know signers can easily batch numerous VRF outputs into a single proof with these, ala CloudFlare\'s Privacy Pass.  If we employ these VRFs for block production then signers could periodically publish a "sync digest" that consolidated thousands of their past block production VRFs into a single check, which improves syncing speed.  There is also an avenue to batch verify these VRFs by multiply signers, but it requires enlarging the VRF output and proofs from from 96 to 128 bytes.')),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("p",{parentName:"li"},"Small curve of BLS12-381 (48 byte public keys, 96 byte signatures)"),(0,i.kt)("p",{parentName:"li"},"Aggregated signatures verify can faster when using this key if the signer set for a particular message is large but irregularly composed, as in GRANDPA.  Actual signatures are slower than the opposite orientation, and non-constant time extension field arithmetic makes them even slower, or more risky.  Aggregating signatures on the same message like this incurs malleability risks too.  We also envision using this scheme in some fishermen schemes."),(0,i.kt)("p",{parentName:"li"},"We should consider ",(0,i.kt)("a",{parentName:"p",href:"https://eprint.iacr.org/2017/437"},"slothful reduction")," as discussed in ",(0,i.kt)("a",{parentName:"p",href:"https://github.com/zkcrypto/pairing/issues/98"},"https://github.com/zkcrypto/pairing/issues/98")," for these eventually, but initially key splitting should provide solid protection against timing attacks, but with even slower signature speed.")),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("p",{parentName:"li"},"Big curve of BLS12-381 (96 bytes public keys, 48 byte signatures) (optional)"),(0,i.kt)("p",{parentName:"li"},"Aggregated signatures in which we verify many messages by the same signer verify considerably faster when using this key.  We might use these for block production VRFs because they aggregating over the same signer sounds useful for syncing.  Initially, we envisioned aggregation being useful for some VRF non-winner proofs designs, but our new non-winner proof design mostly avoids this requirement.  Right now, we favor the Ristretto Schnorr VRF for block production because individual instances verify faster and it provides rather extreme batching over the same signer already."),(0,i.kt)("p",{parentName:"li"},'We also expect faster aggregate verification from these when signer sets get repeated frequently, so conceivably these make sense for some settings in which small curve keys initially sound optimal.  We envision signature aggregation being "wild" in GRANDPA, so the small curve key still sounds best there.')),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("p",{parentName:"li"},"Authentication key for the transport layer."),(0,i.kt)("p",{parentName:"li"},"We might ideally include node identity form libp2p, but secio handles authentication poorly (",(0,i.kt)("a",{parentName:"p",href:"https://forum.web3.foundation/t/transport-layer-authentication-libp2ps-secio/69"},"see the secio discussion"),")."))),(0,i.kt)("p",null,"A session public key record has a prefix consisting of the above three keys, along with a certificate from the validator operator on the Ristretto Schnorr public key and some previous block hash and height.  We follow this prefix with a first signature block consisting two BLS signatures on the prefix, one by each the BLS keys.  We close the session public key record with a second signature block consisting of a Ristretto Schnorr signature on both the prefix and first signature block.  In this way, we may rotate our BLS12-381 keys without rotating our Ristretto Schnorr public key, possibly buying us some forward security."),(0,i.kt)("p",null,"We include the recent block hash in the certificate, so that if the chain were trusted for proofs-of-possession then attackers cannot place rogue keys that attack honestly created session keys created after their fork.  We recommend against trusting the chain for proofs-of-possession however because including some recent block hash like this only helps against longer range attacks. "),(0,i.kt)("p",null,"We still lack any wonderful aggregation strategy for block production VRFs, so they may default to Ristretto Schnorr VRFs.  In this case, the Ristretto Schnorr session key component living longer also help minimize attacks on our random beacon."))}h.isMDXComponent=!0}}]);