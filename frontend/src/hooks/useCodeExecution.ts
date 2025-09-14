import { useState, useCallback } from 'react';
import { ExecutionResult, TestCase, SupportedLanguage } from '../types/coding';
import { codeExecutionService } from '../services/codeExecutionService';

interface UseCodeExecutionOptions {
  onExecutionStart?: () => void;
  onExecutionComplete?: (result: ExecutionResult) => void;
  onExecutionError?: (error: Error) => void;
}

export const useCodeExecution = (options: UseCodeExecutionOptions = {}) => {
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const executeCode = useCallback(async (
    code: string,
    language: SupportedLanguage,
    input?: string
  ): Promise<ExecutionResult> => {
    setIsExecuting(true);
    setError(null);
    options.onExecutionStart?.();

    try {
      const result = await codeExecutionService.executeCode({
        code,
        language,
        input,
      });

      setExecutionResult(result);
      options.onExecutionComplete?.(result);
      return result;
    } catch (err) {
      const error = err as Error;
      setError(error.message);
      options.onExecutionError?.(error);
      
      const errorResult: ExecutionResult = {
        success: false,
        output: '',
        error: error.message,
        executionTime: 0,
        memoryUsage: 0,
      };
      
      setExecutionResult(errorResult);
      return errorResult;
    } finally {
      setIsExecuting(false);
    }
  }, [options]);

  const runTests = useCallback(async (
    code: string,
    language: SupportedLanguage,
    testCases: TestCase[]
  ): Promise<ExecutionResult> => {
    setIsExecuting(true);
    setError(null);
    options.onExecutionStart?.();

    try {
      const result = await codeExecutionService.runTests({
        code,
        language,
        testCases,
      });

      setExecutionResult(result);
      options.onExecutionComplete?.(result);
      return result;
    } catch (err) {
      const error = err as Error;
      setError(error.message);
      options.onExecutionError?.(error);
      
      const errorResult: ExecutionResult = {
        success: false,
        output: '',
        error: error.message,
        executionTime: 0,
        memoryUsage: 0,
      };
      
      setExecutionResult(errorResult);
      return errorResult;
    } finally {
      setIsExecuting(false);
    }
  }, [options]);

  const validateSyntax = useCallback(async (
    code: string,
    language: SupportedLanguage
  ): Promise<{ valid: boolean; errors?: string[] }> => {
    try {
      return await codeExecutionService.validateSyntax(code, language);
    } catch (err) {
      const error = err as Error;
      return {
        valid: false,
        errors: [error.message],
      };
    }
  }, []);

  const clearResults = useCallback(() => {
    setExecutionResult(null);
    setError(null);
  }, []);

  return {
    isExecuting,
    executionResult,
    error,
    executeCode,
    runTests,
    validateSyntax,
    clearResults,
  };
};