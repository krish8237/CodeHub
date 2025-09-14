import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Chip,
  Divider,
} from '@mui/material';
import {
  PlayArrow as RunIcon,
  BugReport as TestIcon,
  CheckCircle as PassIcon,
  Error as FailIcon,
  AccessTime as TimeIcon,
  Memory as MemoryIcon,
} from '@mui/icons-material';
import { ExecutionResult, TestCaseResult } from '../../types/coding';

interface CodeExecutionPanelProps {
  onRunCode: () => Promise<ExecutionResult>;
  onRunTests: () => Promise<ExecutionResult>;
  isExecuting: boolean;
  executionResult: ExecutionResult | null;
  height?: string | number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`execution-tabpanel-${index}`}
      aria-labelledby={`execution-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 2 }}>{children}</Box>}
    </div>
  );
};

export const CodeExecutionPanel: React.FC<CodeExecutionPanelProps> = ({
  onRunCode,
  onRunTests,
  isExecuting,
  executionResult,
  height = '300px',
}) => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleRunCode = async () => {
    try {
      await onRunCode();
      setActiveTab(0); // Switch to output tab
    } catch (error) {
      console.error('Error running code:', error);
    }
  };

  const handleRunTests = async () => {
    try {
      await onRunTests();
      setActiveTab(1); // Switch to test results tab
    } catch (error) {
      console.error('Error running tests:', error);
    }
  };

  const formatExecutionTime = (time: number): string => {
    if (time < 1000) {
      return `${time}ms`;
    }
    return `${(time / 1000).toFixed(2)}s`;
  };

  const formatMemoryUsage = (memory: number): string => {
    if (memory < 1024) {
      return `${memory}B`;
    } else if (memory < 1024 * 1024) {
      return `${(memory / 1024).toFixed(2)}KB`;
    }
    return `${(memory / (1024 * 1024)).toFixed(2)}MB`;
  };

  const getTestResultsSummary = (testResults: TestCaseResult[]) => {
    const passed = testResults.filter(result => result.passed).length;
    const total = testResults.length;
    return { passed, total };
  };

  return (
    <Paper
      elevation={1}
      sx={{
        height,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* Action Buttons */}
      <Box
        sx={{
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
          gap: 2,
          alignItems: 'center',
        }}
      >
        <Button
          variant="contained"
          startIcon={isExecuting ? <CircularProgress size={16} /> : <RunIcon />}
          onClick={handleRunCode}
          disabled={isExecuting}
          color="primary"
        >
          Run Code
        </Button>
        <Button
          variant="outlined"
          startIcon={isExecuting ? <CircularProgress size={16} /> : <TestIcon />}
          onClick={handleRunTests}
          disabled={isExecuting}
          color="secondary"
        >
          Run Tests
        </Button>
        
        {executionResult && (
          <Box sx={{ display: 'flex', gap: 1, ml: 'auto' }}>
            <Chip
              icon={<TimeIcon />}
              label={formatExecutionTime(executionResult.executionTime)}
              size="small"
              variant="outlined"
            />
            <Chip
              icon={<MemoryIcon />}
              label={formatMemoryUsage(executionResult.memoryUsage)}
              size="small"
              variant="outlined"
            />
          </Box>
        )}
      </Box>

      {/* Results Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="execution results tabs">
          <Tab label="Output" id="execution-tab-0" aria-controls="execution-tabpanel-0" />
          <Tab 
            label={
              executionResult?.testResults ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  Test Results
                  {(() => {
                    const { passed, total } = getTestResultsSummary(executionResult.testResults);
                    return (
                      <Chip
                        size="small"
                        label={`${passed}/${total}`}
                        color={passed === total ? 'success' : 'error'}
                        variant="outlined"
                      />
                    );
                  })()}
                </Box>
              ) : (
                'Test Results'
              )
            }
            id="execution-tab-1"
            aria-controls="execution-tabpanel-1"
          />
        </Tabs>
      </Box>

      {/* Tab Content */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <TabPanel value={activeTab} index={0}>
          {executionResult ? (
            <Box>
              {executionResult.error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                    {executionResult.error}
                  </Typography>
                </Alert>
              )}
              
              {executionResult.output && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Output:
                  </Typography>
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 2,
                      backgroundColor: 'grey.50',
                      fontFamily: 'monospace',
                      fontSize: '0.875rem',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      maxHeight: '200px',
                      overflow: 'auto',
                    }}
                  >
                    {executionResult.output || 'No output'}
                  </Paper>
                </Box>
              )}
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary">
              Click "Run Code" to see the output of your program.
            </Typography>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          {executionResult?.testResults ? (
            <Box>
              {executionResult.testResults.map((result, index) => (
                <Box key={result.testCaseId} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    {result.passed ? (
                      <PassIcon color="success" fontSize="small" />
                    ) : (
                      <FailIcon color="error" fontSize="small" />
                    )}
                    <Typography variant="subtitle2">
                      Test Case {index + 1}
                    </Typography>
                    <Chip
                      size="small"
                      label={formatExecutionTime(result.executionTime)}
                      variant="outlined"
                    />
                  </Box>
                  
                  {result.error && (
                    <Alert severity="error" sx={{ mb: 1 }}>
                      <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                        {result.error}
                      </Typography>
                    </Alert>
                  )}
                  
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Expected Output:
                      </Typography>
                      <Paper
                        variant="outlined"
                        sx={{
                          p: 1,
                          backgroundColor: 'grey.50',
                          fontFamily: 'monospace',
                          fontSize: '0.75rem',
                          whiteSpace: 'pre-wrap',
                          minHeight: '40px',
                        }}
                      >
                        {result.expectedOutput}
                      </Paper>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Actual Output:
                      </Typography>
                      <Paper
                        variant="outlined"
                        sx={{
                          p: 1,
                          backgroundColor: result.passed ? 'success.50' : 'error.50',
                          fontFamily: 'monospace',
                          fontSize: '0.75rem',
                          whiteSpace: 'pre-wrap',
                          minHeight: '40px',
                        }}
                      >
                        {result.actualOutput}
                      </Paper>
                    </Box>
                  </Box>
                  
                  {index < executionResult.testResults.length - 1 && (
                    <Divider sx={{ mt: 2 }} />
                  )}
                </Box>
              ))}
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary">
              Click "Run Tests" to see test case results.
            </Typography>
          )}
        </TabPanel>
      </Box>
    </Paper>
  );
};