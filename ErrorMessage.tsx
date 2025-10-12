
import React from 'react';

interface ErrorMessageProps {
  message: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message }) => {
  return (
    <div className="bg-red-900/50 border-2 border-red-500 text-red-300 p-6 rounded-xl shadow-lg flex flex-col items-center text-center gap-4">
      <div className="text-2xl font-bold">Error</div>
      <p className="max-w-md">{message}</p>
    </div>
  );
};
