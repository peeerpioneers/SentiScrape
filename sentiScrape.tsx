
import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { TickerInput } from './components/TickerInput';
import { SentimentTable } from './components/SentimentTable';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorMessage } from './components/ErrorMessage';
import { InitialStateMessage } from './components/InitialStateMessage';
import type { SentimentData } from './types';
import { fetchSentimentData } from './services/geminiService';

const App: React.FC = () => {
  const [sentimentData, setSentimentData] = useState<SentimentData[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentTicker, setCurrentTicker] = useState<string>('');

  const handleFetchSentiment = useCallback(async (ticker: string) => {
    if (!ticker) return;
    
    setIsLoading(true);
    setError(null);
    setSentimentData(null);
    setCurrentTicker(ticker.toUpperCase());

    try {
      const data = await fetchSentimentData(ticker);
      if (data.length === 0) {
        setError(`No sentiment data could be generated for the ticker "${ticker}". It might be invalid or have no recent activity.`);
      } else {
        setSentimentData(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200 font-sans flex flex-col items-center p-4 sm:p-6 lg:p-8">
      <main className="w-full max-w-5xl mx-auto flex flex-col gap-8">
        <Header />
        <TickerInput onFetch={handleFetchSentiment} isLoading={isLoading} />
        
        <div className="mt-4">
          {isLoading && <LoadingSpinner ticker={currentTicker} />}
          {error && <ErrorMessage message={error} />}
          {!isLoading && !error && sentimentData && <SentimentTable data={sentimentData} />}
          {!isLoading && !error && !sentimentData && <InitialStateMessage />}
        </div>
      </main>
    </div>
  );
};

export default App;
