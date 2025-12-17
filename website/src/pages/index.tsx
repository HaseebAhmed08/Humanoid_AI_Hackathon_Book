import type { ReactNode } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

// Module card data
const modules = [
  {
    title: 'Module 1: ROS 2 Foundations',
    weeks: 'Weeks 1-5',
    description: 'Build your foundation in robot programming with ROS 2. Learn nodes, topics, services, and robot descriptions.',
    link: '/docs/module-1-ros/intro',
    icon: '🤖',
  },
  {
    title: 'Module 2: Simulation',
    weeks: 'Weeks 6-8',
    description: 'Master physics simulation with Gazebo and NVIDIA Isaac Sim. Test your robots in virtual environments.',
    link: '/docs/module-2-simulation/intro',
    icon: '🎮',
  },
  {
    title: 'Module 3: Digital Twin',
    weeks: 'Weeks 9-11',
    description: 'Create virtual replicas of physical robots. Learn real-time synchronization and USD assets.',
    link: '/docs/module-3-digital-twin/intro',
    icon: '🔄',
  },
  {
    title: 'Module 4: AI Brain',
    weeks: 'Weeks 12-16',
    description: 'Integrate AI into your robots. Voice control, vision understanding, and cognitive planning.',
    link: '/docs/module-4-ai-brain/intro',
    icon: '🧠',
  },
];

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link className="button button--secondary button--lg" to="/docs/intro">
            Start Learning
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            to="/docs/module-1-ros/intro"
            style={{ marginLeft: '1rem' }}
          >
            Jump to Module 1
          </Link>
        </div>
      </div>
    </header>
  );
}

function ModuleCard({ title, weeks, description, link, icon }: {
  title: string;
  weeks: string;
  description: string;
  link: string;
  icon: string;
}) {
  return (
    <div className={clsx('col col--3', styles.moduleCard)}>
      <div className="card">
        <div className="card__header">
          <div className={styles.moduleIcon}>{icon}</div>
          <Heading as="h3">{title}</Heading>
          <span className={styles.weeksBadge}>{weeks}</span>
        </div>
        <div className="card__body">
          <p>{description}</p>
        </div>
        <div className="card__footer">
          <Link className="button button--primary button--block" to={link}>
            Start Module
          </Link>
        </div>
      </div>
    </div>
  );
}

function ModulesSection() {
  return (
    <section className={styles.modules}>
      <div className="container">
        <div className="text--center margin-bottom--xl">
          <Heading as="h2">Learning Modules</Heading>
          <p className={styles.modulesSubtitle}>
            Progress through four comprehensive modules to master humanoid robotics
          </p>
        </div>
        <div className="row">
          {modules.map((props, idx) => (
            <ModuleCard key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

function FeaturesSection() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          <div className="col col--4">
            <div className="text--center">
              <div className={styles.featureIcon}>💬</div>
              <Heading as="h3">AI Chatbot</Heading>
              <p>
                Ask questions about any topic and get instant, accurate answers powered by RAG
                technology.
              </p>
            </div>
          </div>
          <div className="col col--4">
            <div className="text--center">
              <div className={styles.featureIcon}>🎯</div>
              <Heading as="h3">Personalized Learning</Heading>
              <p>
                Content adapts to your experience level and hardware. Beginners and experts get
                tailored paths.
              </p>
            </div>
          </div>
          <div className="col col--4">
            <div className="text--center">
              <div className={styles.featureIcon}>🌐</div>
              <Heading as="h3">Urdu Translation</Heading>
              <p>
                Translate any chapter to Urdu with one click. Technical terms are preserved in
                brackets.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function PrerequisitesSection() {
  return (
    <section className={styles.prerequisites}>
      <div className="container">
        <div className="row">
          <div className="col col--6">
            <Heading as="h2">Prerequisites</Heading>
            <ul>
              <li>Basic Python programming knowledge</li>
              <li>Linux familiarity (Ubuntu 22.04 recommended)</li>
              <li>Git version control basics</li>
              <li>Curiosity about robotics!</li>
            </ul>
          </div>
          <div className="col col--6">
            <Heading as="h2">Hardware Recommendations</Heading>
            <table>
              <thead>
                <tr>
                  <th>Component</th>
                  <th>Minimum</th>
                  <th>Recommended</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>RAM</td>
                  <td>8 GB</td>
                  <td>16+ GB</td>
                </tr>
                <tr>
                  <td>Storage</td>
                  <td>50 GB</td>
                  <td>100+ GB SSD</td>
                </tr>
                <tr>
                  <td>GPU</td>
                  <td>Integrated</td>
                  <td>NVIDIA RTX</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title="Home" description={siteConfig.tagline}>
      <HomepageHeader />
      <main>
        <ModulesSection />
        <FeaturesSection />
        <PrerequisitesSection />
      </main>
    </Layout>
  );
}
