import React from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PhishingIcon from '@mui/icons-material/PhishingOutlined';
import SecurityIcon from '@mui/icons-material/SecurityOutlined';
import WarningIcon from '@mui/icons-material/WarningAmberOutlined';

const ThreatAwareness = () => {
  const threats = [
    {
      title: 'Phishing Attacks',
      icon: <PhishingIcon fontSize="large" />,
      description:
        'Phishing attacks attempt to steal your personal information by masquerading as legitimate websites or services.',
      tips: [
        'Never click on suspicious links in emails',
        'Check the URL carefully before entering credentials',
        'Be wary of urgent requests for personal information',
        'Look for SSL certificates (https://) on websites',
      ],
    },
    {
      title: 'Deepfake Media',
      icon: <SecurityIcon fontSize="large" />,
      description:
        'AI-generated fake media can be used to spread misinformation or impersonate individuals.',
      tips: [
        'Verify sources of viral media content',
        'Look for visual inconsistencies',
        'Cross-reference with trusted news sources',
        'Use our deepfake detection tool for analysis',
      ],
    },
    {
      title: 'Financial Fraud',
      icon: <WarningIcon fontSize="large" />,
      description:
        'Cybercriminals use various techniques to commit financial fraud and steal money.',
      tips: [
        'Use strong, unique passwords for financial accounts',
        'Enable two-factor authentication',
        'Monitor your accounts regularly',
        'Never share banking credentials via email',
      ],
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Threat Awareness
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {threats.map((threat, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    mb: 2,
                    color: 'primary.main',
                  }}
                >
                  {threat.icon}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    {threat.title}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {threat.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Typography variant="h5" gutterBottom>
        Detailed Security Guidelines
      </Typography>

      {threats.map((threat, index) => (
        <Accordion key={index}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">{threat.title} Prevention</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <ul>
              {threat.tips.map((tip, tipIndex) => (
                <li key={tipIndex}>
                  <Typography variant="body2">{tip}</Typography>
                </li>
              ))}
            </ul>
          </AccordionDetails>
        </Accordion>
      ))}

      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Stay Protected
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Remember to regularly update your software, use strong passwords, and
            stay informed about the latest cybersecurity threats. Our AI Defense
            System continuously monitors and protects you from emerging threats.
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
};

export default ThreatAwareness;
