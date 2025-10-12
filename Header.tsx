
import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="text-center w-full">
      <h1 className="text-4xl sm:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600 mb-2">
        SentiScrape
      </h1>
      <p className="text-md sm:text-lg text-slate-400 max-w-2xl mx-auto">
        Analyze daily stock sentiment with simulated filtering to weed out bots and repetitive comments for a clearer view.
      </p>
    </header>
  );
};
