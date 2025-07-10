// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');
const math = require('remark-math');
const katex = require('rehype-katex');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Research at Web3 Foundation',
  tagline: 'Confronting the most difficult research problems standing between us and Web3.',
  favicon: 'img/favicon-32x32.png',
  url: 'https://research.web3.foundation/',
  baseUrl: '/',
  organizationName: 'w3f', // Usually your GitHub org/user name.
  projectName: 'research', // Usually your repo name.
  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',
  trailingSlash: false,

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          remarkPlugins: [math],
          rehypePlugins: [[katex, { macros: {
            "\\skvrf": "\\mathsf{sk}^v",
            "\\pkvrf": "\\mathsf{pk}^v",
            "\\sksgn": "\\mathsf{sk}^s",
            "\\pksgn": "\\mathsf{pk}^s",
            "\\skac": "\\mathsf{sk}^a",
            "\\pkac": "\\mathsf{pk}^a",
            "\\D": "\\Delta",
            "\\A": "\\mathcal{A}",
            "\\vrf": "\\mathsf{vrf}",
            "\\sgn": "\\mathsf{Sign}",
          }}]],
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/w3f/research/blob/master',
          routeBasePath: '/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
        blog: false
      }),
    ],
  ],

  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.13.24/dist/katex.min.css',
      type: 'text/css',
      integrity:
        'sha384-odtC+0UGzzFL/6PNoE8rX/SPcQDXBJ+uRepguP4QkPCm2LBxH3FA3y+fKSiJ+AmM',
      crossorigin: 'anonymous',
    },
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        logo: {
          alt: 'W3F Logo',
          src: 'img/w3f_logo.svg',
        },
        title: 'Research',
        items: [
          {
            type: 'doc',
            docId: 'Polkadot/index',
            position: 'right',
            label: 'Polkadot',
          },
          {
            type: 'doc',
            docId: 'team_members/index',
            position: 'right',
            label: 'Team',
          },
          {
            type: 'doc',
            docId: 'Publications',
            position: 'right',
            label: 'Publications',
          },
          {
            href: 'https://github.com/w3f/research',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'More Info',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/w3f/research',
              },
              {
                label: 'Website',
                href: 'https://web3.foundation/',
              },
              {
                label: 'Privacy Policy',
                to: 'Support%20Docs/privacy_policy',
              },
              {
                label: 'Legal Disclosures',
                to: 'https://web3.foundation/legal-disclosures/',
              },
            ],
          }, 
          {
            title: 'Connect',
            items: [
              {
                label: 'Twitter',
                href: 'https://twitter.com/Web3foundation',
              },
            ],
          },
        ],
        copyright: `© ${new Date().getFullYear()} Web3 Foundation`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: true,
      },
    }),
};

module.exports = config;
