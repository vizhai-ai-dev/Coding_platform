import React, { useState } from 'react';
import { Paper, Typography, Box, Divider, Chip, Tabs, Tab, Button, Badge } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import TimerIcon from '@mui/icons-material/Timer';
import MemoryIcon from '@mui/icons-material/Memory';
import AddIcon from '@mui/icons-material/Add';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';

interface TestResult {
  passed: boolean;
  input: string;
  expectedOutput: string;
  actualOutput: string;
  executionTime: number;
  memoryUsage: number;
  is_hidden?: boolean;
}

interface OutputConsoleProps {
  testResults: TestResult[];
  overallMetrics: {
    totalTests: number;
    passedTests: number;
    averageTime: number;
    averageMemory: number;
    status?: string;
  };
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`testcase-tabpanel-${index}`}
      aria-labelledby={`testcase-tab-${index}`}
      {...other}
      style={{ height: 'calc(100% - 48px)', overflow: 'auto', padding: '16px' }}
    >
      {value === index && children}
    </div>
  );
}

const OutputConsole: React.FC<OutputConsoleProps> = ({ testResults, overallMetrics }) => {
  const [currentTab, setCurrentTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  // If we don't have any test results yet, show a placeholder
  if (testResults.length === 0) {
    return (
      <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', p: 0 }}>
          <Tabs value={0} aria-label="testcase tabs">
            <Tab label="Testcase" />
            <Tab label="Test Result" disabled />
          </Tabs>
        </Box>
        <Box sx={{ p: 3, textAlign: 'center', color: 'text.secondary', flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
          <Typography variant="body1" gutterBottom>
            Run your code to see the test results
          </Typography>
          <Button variant="outlined" startIcon={<AddIcon />}>
            Add Custom Testcase
          </Button>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Summary section */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h6" component="div">
            {overallMetrics.status || (overallMetrics.passedTests === overallMetrics.totalTests ? "Accepted" : "Wrong Answer")}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {overallMetrics.passedTests} / {overallMetrics.totalTests} test cases passed
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Chip 
            icon={<TimerIcon />} 
            label={`Avg Runtime: ${(overallMetrics.averageTime || 0).toFixed(2)} ms`} 
            variant="outlined"
            size="small"
          />
          <Chip 
            icon={<MemoryIcon />} 
            label={`Avg Memory: ${((overallMetrics.averageMemory || 0) / 1024).toFixed(2)} MB`} 
            variant="outlined"
            size="small"
          />
        </Box>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', p: 0 }}>
        <Tabs 
          value={currentTab} 
          onChange={handleTabChange} 
          aria-label="testcase tabs"
          variant="scrollable"
          scrollButtons="auto"
        >
          {testResults.map((result, idx) => (
            <Tab 
              key={idx} 
              label={
                result.is_hidden ? (
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <VisibilityOffIcon fontSize="small" sx={{ mr: 0.5 }} />
                    <span>Case {idx + 1}</span>
                  </Box>
                ) : `Case ${idx + 1}`
              }
              icon={result.passed ? <CheckCircleIcon color="success" fontSize="small" /> : <ErrorIcon color="error" fontSize="small" />}
              iconPosition="end"
            />
          ))}
        </Tabs>
      </Box>

      {testResults.map((result, index) => (
        <TabPanel key={index} value={currentTab} index={index}>
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Input:
            </Typography>
            <Box sx={{ bgcolor: 'background.paper', p: 2, borderRadius: 1, fontFamily: 'monospace', border: '1px solid', borderColor: 'divider', mb: 2 }}>
              {result.input}
            </Box>
            
            {result.is_hidden && !result.passed ? (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Expected output is hidden for this test case
              </Typography>
            ) : (
              <>
                <Typography variant="subtitle2" gutterBottom>
                  Expected Output:
                </Typography>
                <Box sx={{ bgcolor: 'background.paper', p: 2, borderRadius: 1, fontFamily: 'monospace', border: '1px solid', borderColor: 'divider', mb: 2 }}>
                  {result.expectedOutput}
                </Box>
              </>
            )}
            
            <Typography variant="subtitle2" gutterBottom>
              Your Output:
            </Typography>
            <Box sx={{ bgcolor: 'background.paper', p: 2, borderRadius: 1, fontFamily: 'monospace', border: '1px solid', borderColor: 'divider', mb: 2 }}>
              {result.actualOutput}
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 2 }}>
              {result.passed ? (
                <Chip 
                  icon={<CheckCircleIcon />} 
                  label="Accepted" 
                  color="success"
                />
              ) : (
                <Chip 
                  icon={<ErrorIcon />} 
                  label="Wrong Answer" 
                  color="error"
                />
              )}
              <Chip 
                icon={<TimerIcon />} 
                label={`Runtime: ${(result.executionTime || 0).toFixed(2)} ms`} 
                variant="outlined"
              />
              <Chip 
                icon={<MemoryIcon />} 
                label={`Memory: ${((result.memoryUsage || 0) / 1024).toFixed(2)} MB`} 
                variant="outlined"
              />
              {result.is_hidden && (
                <Chip 
                  icon={<VisibilityOffIcon />} 
                  label="Hidden Test" 
                  variant="outlined"
                />
              )}
            </Box>
          </Box>
        </TabPanel>
      ))}
    </Paper>
  );
};

export default OutputConsole; 