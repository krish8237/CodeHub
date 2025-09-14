import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  IconButton,
  Tooltip,
  Alert,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as ResetIcon,
  Fullscreen as FullscreenIcon,
  FullscreenExit as FullscreenExitIcon,
} from '@mui/icons-material';
import { MonacoCodeEditor } from './MonacoCodeEditor';
import { CodeExecutionPanel } from './CodeExecutionPanel';
import { LanguageSelector } from './LanguageSelector';
import { 
  CodingQuestion, 
  ExecutionResult, 
  SupportedLanguage, 
  CodeSubmission 
} from '../../types/coding';
import { getDefaultCodeForLanguage } from '../../constants/languages';

interface CodingInterfaceProps {
  question: CodingQuestion;
  onCodeSubmit?: (submission: CodeSubmission) => void;
  onAutoSave?: (code: string) => void;
  initialCode?: string;
  readOnly?: boolean;
  showLanguageSelector?: boolean;
  allowedLanguages?: SupportedLanguage[];
}

export const CodingInterface: React.FC<CodingInterfaceProps> = ({
  question,
  onCodeSubmit,
  onAutoSave,
  initialCode,
  readOnly = false,
  showLanguageSelector = true,
  allowedLanguages,
}) => {
  const [code, setCode] = useState(initialCode || question.starterCode || '');
  const [language, setLanguage] = useState<SupportedLanguage>(question.language as SupportedLanguage);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout>();
  const lastSavedCodeRef = useRef(code);

  // Auto-save functionality
  useEffect(() => {
    if (code !== lastSavedCodeRef.current && onAutoSave) {
      setHasUnsavedChanges(true);
      
      // Clear existing timeout
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
      
      // Set new timeout for auto-save
      autoSaveTimeoutRef.current = setTimeout(() => {
        onAutoSave(code);
        lastSavedCodeRef.current = code;
        setHasUnsavedChanges(false);
      }, 2000); // Auto-save after 2 seconds of inactivity
    }
    
    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, [code, onAutoSave]);

  // Handle language change
  const handleLanguageChange = useCallback((newLanguage: SupportedLanguage) => {
    if (newLanguage !== language) {
      setLanguage(newLanguage);
      // Reset to default code for new language if current code is empty or default
      const defaultCode = getDefaultCodeForLanguage(newLanguage);
      if (!code.trim() || code === getDefaultCodeForLanguage(language)) {
        setCode(defaultCode);
      }
    }
  }, [language, code]);

  // Handle code change
  const handleCodeChange = useCallback((newCode: string) => {
    setCode(newCode);
  }, []);

  // Code execution using the service
  const handleRunCode = useCallback(async (): Promise<ExecutionResult> => {
    setIsExecuting(true);
    
    try {
      // For demo purposes, we'll use mock data since the backend might not be running
      // In production, this would use: codeExecutionService.executeCode({ code, language })
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock execution result with more realistic output
      const result: ExecutionResult = {
        success: true,
        output: `Code executed successfully!\n\nOutput:\n${getMockOutput(code, language)}`,
        executionTime: 150 + Math.random() * 200,
        memoryUsage: 1024 * (512 + Math.random() * 256), // 512KB - 768KB
      };
      
      setExecutionResult(result);
      return result;
    } catch (error) {
      const errorResult: ExecutionResult = {
        success: false,
        output: '',
        error: 'Execution failed: ' + (error as Error).message,
        executionTime: 0,
        memoryUsage: 0,
      };
      
      setExecutionResult(errorResult);
      return errorResult;
    } finally {
      setIsExecuting(false);
    }
  }, [code, language]);

  // Test execution using the service
  const handleRunTests = useCallback(async (): Promise<ExecutionResult> => {
    setIsExecuting(true);
    
    try {
      // For demo purposes, we'll use mock data since the backend might not be running
      // In production, this would use: codeExecutionService.runTests({ code, language, testCases: question.testCases })
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock test results with realistic pass/fail logic
      const result: ExecutionResult = {
        success: true,
        output: 'All tests completed',
        executionTime: 300 + Math.random() * 200,
        memoryUsage: 1024 * (768 + Math.random() * 256), // 768KB - 1MB
        testResults: question.testCases.map((testCase, index) => {
          const passed = Math.random() > 0.2; // 80% pass rate for demo
          return {
            testCaseId: testCase.id,
            passed,
            actualOutput: passed ? testCase.expectedOutput : `Incorrect output for test ${index + 1}`,
            expectedOutput: testCase.expectedOutput,
            executionTime: 50 + Math.random() * 100,
          };
        }),
      };
      
      setExecutionResult(result);
      return result;
    } catch (error) {
      const errorResult: ExecutionResult = {
        success: false,
        output: '',
        error: 'Test execution failed: ' + (error as Error).message,
        executionTime: 0,
        memoryUsage: 0,
      };
      
      setExecutionResult(errorResult);
      return errorResult;
    } finally {
      setIsExecuting(false);
    }
  }, [question.testCases, code, language]);

  // Helper function to generate mock output based on language
  const getMockOutput = (code: string, language: SupportedLanguage): string => {
    if (code.includes('print(') || code.includes('console.log(') || code.includes('System.out.println(') || code.includes('cout <<') || code.includes('Console.WriteLine(') || code.includes('fmt.Println(') || code.includes('println!(')) {
      return 'Hello, World!\n42\nCode execution completed.';
    }
    return 'Program executed successfully.';
  };

  // Handle manual save
  const handleSave = useCallback(() => {
    if (onCodeSubmit) {
      const submission: CodeSubmission = {
        questionId: question.id,
        code,
        language,
        timestamp: new Date(),
      };
      onCodeSubmit(submission);
      setHasUnsavedChanges(false);
    }
  }, [code, language, question.id, onCodeSubmit]);

  // Handle reset to starter code
  const handleReset = useCallback(() => {
    const defaultCode = question.starterCode || getDefaultCodeForLanguage(language);
    setCode(defaultCode);
    setExecutionResult(null);
  }, [question.starterCode, language]);

  // Toggle fullscreen
  const handleToggleFullscreen = useCallback(() => {
    setIsFullscreen(!isFullscreen);
  }, [isFullscreen]);

  return (
    <Box
      sx={{
        height: isFullscreen ? '100vh' : '600px',
        display: 'flex',
        flexDirection: 'column',
        position: isFullscreen ? 'fixed' : 'relative',
        top: isFullscreen ? 0 : 'auto',
        left: isFullscreen ? 0 : 'auto',
        right: isFullscreen ? 0 : 'auto',
        bottom: isFullscreen ? 0 : 'auto',
        zIndex: isFullscreen ? 9999 : 'auto',
        backgroundColor: 'background.default',
      }}
    >
      {/* Header */}
      <Paper
        elevation={1}
        sx={{
          p: 2,
          borderRadius: isFullscreen ? 0 : 1,
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="h6" component="h2">
            {question.title}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {hasUnsavedChanges && (
              <Alert severity="info" sx={{ py: 0, px: 1 }}>
                <Typography variant="caption">Auto-saving...</Typography>
              </Alert>
            )}
            
            {showLanguageSelector && (
              <LanguageSelector
                value={language}
                onChange={handleLanguageChange}
                disabled={readOnly}
                allowedLanguages={allowedLanguages}
              />
            )}
            
            <Tooltip title="Save Code">
              <IconButton onClick={handleSave} disabled={readOnly}>
                <SaveIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Reset to Starter Code">
              <IconButton onClick={handleReset} disabled={readOnly}>
                <ResetIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}>
              <IconButton onClick={handleToggleFullscreen}>
                {isFullscreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        {question.description && (
          <>
            <Divider sx={{ my: 1 }} />
            <Typography variant="body2" color="text.secondary">
              {question.description}
            </Typography>
          </>
        )}
      </Paper>

      {/* Main Content - Split Pane Layout */}
      <Box
        sx={{
          flex: 1,
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1fr 4px 1fr' },
          gridTemplateRows: { xs: '1fr 4px 1fr', md: '1fr' },
          overflow: 'hidden',
          gap: 0,
        }}
      >
        {/* Code Editor */}
        <Box
          sx={{
            minHeight: { xs: '300px', md: 'auto' },
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          <MonacoCodeEditor
            value={code}
            onChange={handleCodeChange}
            language={language}
            height="100%"
            readOnly={readOnly}
          />
        </Box>

        {/* Resizable Divider */}
        <Box
          sx={{
            backgroundColor: 'divider',
            cursor: { xs: 'row-resize', md: 'col-resize' },
            '&:hover': {
              backgroundColor: 'primary.main',
            },
            transition: 'background-color 0.2s',
          }}
        />

        {/* Execution Panel */}
        <Box
          sx={{
            minHeight: { xs: '300px', md: 'auto' },
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          <CodeExecutionPanel
            onRunCode={handleRunCode}
            onRunTests={handleRunTests}
            isExecuting={isExecuting}
            executionResult={executionResult}
            height="100%"
          />
        </Box>
      </Box>
    </Box>
  );
};