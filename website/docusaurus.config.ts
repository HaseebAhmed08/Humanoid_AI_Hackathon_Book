import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Master ROS 2, Simulation, Digital Twins, and AI-Powered Robotics',
  favicon: 'img/favicon.ico',

  // Future flags for Docusaurus v4 compatibility
  future: {
    v4: true,
  },

  // Production URL
  url: 'https://humanoid-robotics-book.github.io',
  baseUrl: '/',

  // GitHub pages deployment config
  organizationName: 'humanoid-robotics-book',
  projectName: 'humanoid-robotics-book.github.io',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',

  // Internationalization
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Show reading time for docs
          showLastUpdateTime: true,
          // Edit URL for the repo
          editUrl:
            'https://github.com/humanoid-robotics-book/humanoid-robotics-book/tree/main/website/',
        },
        blog: false, // Disable blog for now
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Social card image
    image: 'img/social-card.png',

    // Color mode settings
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },

    // Announcement bar (optional)
    announcementBar: {
      id: 'hackathon_project',
      content:
        'This is an educational platform for Physical AI & Humanoid Robotics. <a href="/docs/module-1-ros/intro">Start Learning</a>',
      backgroundColor: '#4f46e5',
      textColor: '#ffffff',
      isCloseable: true,
    },

    // Navigation bar
    navbar: {
      title: 'Physical AI',
      logo: {
        alt: 'Physical AI Logo',
        src: 'img/logo.svg',
      },
      items: [
        // Modules dropdown
        {
          type: 'dropdown',
          label: 'Modules',
          position: 'left',
          items: [
            {
              type: 'doc',
              docId: 'module-1-ros/intro',
              label: 'Module 1: ROS 2 Foundations',
            },
            {
              type: 'doc',
              docId: 'module-2-simulation/intro',
              label: 'Module 2: Simulation',
            },
            {
              type: 'doc',
              docId: 'module-3-digital-twin/intro',
              label: 'Module 3: Digital Twin',
            },
            {
              type: 'doc',
              docId: 'module-4-ai-brain/intro',
              label: 'Module 4: AI Brain',
            },
          ],
        },
        // Direct link to docs
        {
          type: 'docSidebar',
          sidebarId: 'mainSidebar',
          position: 'left',
          label: 'Documentation',
        },
        // Profile link (right side)
        {
          to: '/profile',
          label: 'Profile',
          position: 'right',
        },
        // GitHub link
        {
          href: 'https://github.com/humanoid-robotics-book/humanoid-robotics-book',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },

    // Footer
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Learn',
          items: [
            {
              label: 'Module 1: ROS 2',
              to: '/docs/module-1-ros/intro',
            },
            {
              label: 'Module 2: Simulation',
              to: '/docs/module-2-simulation/intro',
            },
            {
              label: 'Module 3: Digital Twin',
              to: '/docs/module-3-digital-twin/intro',
            },
            {
              label: 'Module 4: AI Brain',
              to: '/docs/module-4-ai-brain/intro',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'ROS 2 Documentation',
              href: 'https://docs.ros.org/en/humble/',
            },
            {
              label: 'Gazebo',
              href: 'https://gazebosim.org/',
            },
            {
              label: 'NVIDIA Isaac Sim',
              href: 'https://developer.nvidia.com/isaac-sim',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/humanoid-robotics-book/humanoid-robotics-book',
            },
            {
              label: 'ROS Discourse',
              href: 'https://discourse.ros.org/',
            },
          ],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} Physical AI & Humanoid Robotics Project. Built with Docusaurus.`,
    },

    // Prism syntax highlighting
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      // Additional languages for robotics content
      // Note: Use 'markup' for XML/HTML, 'c' or 'cpp' for C++
      additionalLanguages: ['python', 'bash', 'yaml', 'json', 'c', 'cpp'],
    },

    // Table of contents
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 4,
    },
  } satisfies Preset.ThemeConfig,

  // Plugins
  plugins: [
    // Add reading time to docs
    async function readingTimePlugin() {
      return {
        name: 'reading-time-plugin',
        // Plugin implementation handled by Docusaurus
      };
    },
  ],

  // Markdown configuration
  // Note: Mermaid diagrams require @docusaurus/theme-mermaid package
  // Install with: npm install @docusaurus/theme-mermaid
  // Then uncomment the themes line below
  // markdown: {
  //   mermaid: true,
  // },
  // themes: ['@docusaurus/theme-mermaid'],
};

export default config;
