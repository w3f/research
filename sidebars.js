/**
 * Creating a sidebar enables you to:
 * - create an ordered group of docs
 * - render a sidebar for each doc of that group
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  sidebar: [
    {
      type: 'doc',
      id: 'research',
    },
    {
      type: 'category',
      label: 'Polkadot',
      link: { type: 'doc', id: 'Polkadot/index' },
      collapsed: false,
      items: [
        {
          type: 'category',
          label: 'Economics',
          link: { type: 'doc', id: 'Polkadot/economics/index' },
          items: [
            {
              type: 'category',
              label: 'Token Economics',
              link: { type: 'doc', id: 'Polkadot/token-economics/index' },
              items: [
              ],
            },
            {
              type: 'category',
              label: 'Academic Research',
              items: [
                'Polkadot/economics/academic-research/validator-selection',
                'Polkadot/economics/academic-research/npos',
                'Polkadot/economics/academic-research/parachain-experiment',
                'Polkadot/economics/academic-research/parachain-theory',
                'Polkadot/economics/academic-research/utilitytokendesign',
                'Polkadot/economics/academic-research/gamification',
              ],
            },
            {
              type: 'category',
              label: 'Applied Research',
              items: [
                'Polkadot/economics/applied-research/rfc17',
                'Polkadot/economics/applied-research/rfc97',
                'Polkadot/economics/applied-research/rfc146',
                'Polkadot/economics/applied-research/rfc10',
                'Polkadot/economics/applied-research/rfc104',
              ],
            },
          ],
        },
        {
          type: 'category',
          label: 'Protocols',
          link: {type:'doc', id:'Polkadot/protocols/index'},
          items: [
            {
              type: 'category',
              label: 'Nominated Proof-of-Stake',
              link: {type:'doc', id:'Polkadot/protocols/NPoS/index'},
              items: [
                'Polkadot/protocols/NPoS/Overview',
                'Polkadot/protocols/NPoS/Paper',
                'Polkadot/protocols/NPoS/Balancing',
              ],
            },
            {
              type: 'category',
              label: 'Block production',
              link: {type:'doc', id:'Polkadot/protocols/block-production/index'},
              items: [
                'Polkadot/protocols/block-production/Babe',
                'Polkadot/protocols/block-production/SASSAFRAS',
                {
              type: 'category',
              label: 'Understanding Sassafras',
              description: 'Understanding Sassafras',
              link: {type:'doc', id:'Polkadot/protocols/Sassafras/index'},
              items: [
                'Polkadot/protocols/Sassafras/sassafras-part-1',
                'Polkadot/protocols/Sassafras/sassafras-part-2',
                'Polkadot/protocols/Sassafras/Sassafras-part-3',
              ],
            },
            'Polkadot/protocols/block-production/ELVES'
              ],
            },
            
            'Polkadot/protocols/finality',
            'Polkadot/protocols/LightClientsBridges',
          ],
        },
        {
          type: 'category',
          label: 'Security',
          link: {type:'doc', id:'Polkadot/security/index'},
          items: [
            {
              type: 'category',
              label: 'Censorship Resistance',
              link: {type:'doc', id:'Polkadot/security/censorship-resistance/index'},
              items: [],
            },
        
            {
              type: 'category',
              label: 'Keys',
              link: {type:'doc', id:'Polkadot/security/keys/index'},
              items: [
                'Polkadot/security/keys/accounts',
                'Polkadot/security/keys/accounts-more',
                'Polkadot/security/keys/staking',
                'Polkadot/security/keys/session',
                'Polkadot/security/keys/creation',
              ],
            },
            {
              type: 'category',
              label: 'Slashing',
              link: {type:'doc', id:'Polkadot/security/slashing/index'},
              items: [
                'Polkadot/security/slashing/amounts',
                'Polkadot/security/slashing/npos',
              ],
            },
          ],
        },
      ]
    },
    {
      type: 'category',
      label: 'Team Members',
      link: {type:'doc', id:'team_members/index'},
      items: [],
    },
    {
      type: 'doc',
      id: 'Publications',
    },
    {
      type: 'doc',
      id: 'Events',
    },
  ],
};

module.exports = sidebars;