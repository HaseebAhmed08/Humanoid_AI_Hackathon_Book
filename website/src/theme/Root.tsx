import React from 'react';
import ChatWidget from '@site/src/components/ChatWidget';

// Default implementation that wraps children
export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  // API URL - hardcoded for now, can be configured via docusaurus.config.ts customFields later
  const apiUrl = 'http://localhost:8000/api';

  return (
    <>
      {children}
      <ChatWidget apiUrl={apiUrl} />
    </>
  );
}
