import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

/**
 * Sidebar configuration for Physical AI & Humanoid Robotics Platform
 *
 * Structure:
 * - Module 1: ROS 2 Foundations (Weeks 1-5)
 * - Module 2: Simulation (Weeks 6-8)
 * - Module 3: Digital Twin (Weeks 9-11)
 * - Module 4: AI Brain (Weeks 12-16)
 */

const sidebars: SidebarsConfig = {
  mainSidebar: [
    // Introduction
    {
      type: 'doc',
      id: 'intro',
      label: 'Getting Started',
    },

    // Module 1: ROS 2 Foundations
    {
      type: 'category',
      label: 'Module 1: ROS 2 Foundations',
      collapsible: true,
      collapsed: false,
      link: {
        type: 'doc',
        id: 'module-1-ros/intro',
      },
      items: [
        'module-1-ros/intro',
        'module-1-ros/nodes-topics',
        // Additional chapters will be added as content is created
      ],
    },

    // Module 2: Simulation
    {
      type: 'category',
      label: 'Module 2: Simulation',
      collapsible: true,
      collapsed: true,
      link: {
        type: 'doc',
        id: 'module-2-simulation/intro',
      },
      items: [
        'module-2-simulation/intro',
        // Additional chapters will be added
      ],
    },

    // Module 3: Digital Twin
    {
      type: 'category',
      label: 'Module 3: Digital Twin',
      collapsible: true,
      collapsed: true,
      link: {
        type: 'doc',
        id: 'module-3-digital-twin/intro',
      },
      items: [
        'module-3-digital-twin/intro',
        // Additional chapters will be added
      ],
    },

    // Module 4: AI Brain
    {
      type: 'category',
      label: 'Module 4: AI Brain',
      collapsible: true,
      collapsed: true,
      link: {
        type: 'doc',
        id: 'module-4-ai-brain/intro',
      },
      items: [
        'module-4-ai-brain/intro',
        // Additional chapters will be added
      ],
    },
  ],
};

export default sidebars;
