import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ArticleInput from '../components/ArticleInput';
import { analyzeArticle, analyzeArticlePdf } from '../services/api';

export default function AnalyzePage() {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (inputType, content) => {
    setIsLoading(true);
    try {
      const data = await analyzeArticle(inputType, content);
      navigate(`/results/${data.run_id}`);
    } catch (err) {
      console.error('Analysis failed:', err);
      setIsLoading(false);
    }
  };

  const handlePdfSubmit = async (file) => {
    setIsLoading(true);
    try {
      const data = await analyzeArticlePdf(file);
      navigate(`/results/${data.run_id}`);
    } catch (err) {
      console.error('PDF analysis failed:', err);
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Policy Impact Analysis</h1>
        <p className="text-[var(--color-text-secondary)]">
          Paste a news article, URL, or upload a PDF to analyze its business impact on the Pakistani market.
        </p>
      </div>
      <ArticleInput onSubmit={handleSubmit} onPdfSubmit={handlePdfSubmit} isLoading={isLoading} />
    </div>
  );
}
