import React, { useState } from 'react';
import { Paper, Typography, Box, Divider, Chip, Tabs, Tab, IconButton } from '@mui/material';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import ShuffleIcon from '@mui/icons-material/Shuffle';

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
      id={`problem-tabpanel-${index}`}
      aria-labelledby={`problem-tab-${index}`}
      {...other}
      style={{ height: 'calc(100% - 48px)', overflow: 'auto' }}
    >
      {value === index && (
        <Box sx={{ p: 2 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

interface ProblemStatementProps {
  problemId: string;
  title: string;
  description: string;
  difficulty: string;
  examples: Array<{
    input: string;
    output: string;
    explanation?: string;
  }>;
  constraints: string[];
  topics?: string[];
  companies?: string[];
}

const ProblemStatement: React.FC<ProblemStatementProps> = ({
  problemId,
  title,
  description,
  difficulty,
  examples,
  constraints,
  topics = [],
  companies = [],
}) => {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const difficultyColor = {
    easy: 'success',
    medium: 'warning',
    hard: 'error',
  }[difficulty.toLowerCase()] || 'default';

  return (
    <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', p: 1, borderBottom: 1, borderColor: 'divider' }}>
        <IconButton size="small" sx={{ mr: 1 }}>
          <ArrowBackIcon fontSize="small" />
        </IconButton>
        <IconButton size="small" sx={{ mr: 1 }}>
          <ArrowForwardIcon fontSize="small" />
        </IconButton>
        <IconButton size="small" sx={{ mr: 1 }}>
          <ShuffleIcon fontSize="small" />
        </IconButton>
        <Box sx={{ flexGrow: 1 }} />
        <IconButton size="small">
          <FullscreenIcon fontSize="small" />
        </IconButton>
      </Box>
      <Tabs value={tabValue} onChange={handleTabChange} aria-label="problem statement tabs">
        <Tab label="Description" />
        <Tab label="Editorial" />
      </Tabs>
      <TabPanel value={tabValue} index={0}>
        <Typography variant="h5" gutterBottom>
          {problemId}. {title}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <Chip 
            label={difficulty.charAt(0).toUpperCase() + difficulty.slice(1)} 
            color={difficultyColor as any} 
            size="small" 
            variant="outlined" 
          />
          {topics.map((topic, index) => (
            <Chip key={index} label={topic} size="small" variant="outlined" />
          ))}
        </Box>
        
        <Typography variant="body1" paragraph style={{ whiteSpace: 'pre-line' }}>
          {description}
        </Typography>
        
        <Typography variant="h6" gutterBottom>
          Examples:
        </Typography>
        
        {examples.map((example, index) => (
          <Box key={index} sx={{ mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Example {index + 1}:
            </Typography>
            <Box sx={{ bgcolor: 'background.paper', p: 2, borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="body2" component="div" sx={{ fontFamily: 'monospace', mb: 1 }}>
                <strong>Input:</strong> {example.input}
              </Typography>
              <Typography variant="body2" component="div" sx={{ fontFamily: 'monospace', mb: example.explanation ? 1 : 0 }}>
                <strong>Output:</strong> {example.output}
              </Typography>
              {example.explanation && (
                <Typography variant="body2" component="div" sx={{ mt: 1 }}>
                  <strong>Explanation:</strong> {example.explanation}
                </Typography>
              )}
            </Box>
          </Box>
        ))}
        
        <Typography variant="h6" gutterBottom>
          Constraints:
        </Typography>
        <Box component="ul" sx={{ pl: 2, mb: 3 }}>
          {constraints.map((constraint, index) => (
            <Typography component="li" variant="body2" key={index} sx={{ fontFamily: 'monospace', mb: 0.5 }}>
              {constraint}
            </Typography>
          ))}
        </Box>
        
        {companies.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" gutterBottom>
              Companies
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {companies.map((company, index) => (
                <Chip key={index} label={company} size="small" variant="outlined" />
              ))}
            </Box>
          </>
        )}
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        <Typography variant="body1">
          Editorial content and solution explanation will appear here.
        </Typography>
      </TabPanel>
    </Paper>
  );
};

export default ProblemStatement; 