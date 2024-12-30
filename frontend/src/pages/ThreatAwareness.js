import React from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Security as SecurityIcon,
} from '@mui/icons-material';

const ThreatAwareness = () => {
  const threats = [
    {
      title: 'Phishing Attacks',
      icon: <SecurityIcon />,
      description: 'Learn how to identify and protect against phishing attempts',
      details: [
        'Check sender email addresses carefully',
        'Be wary of urgent or threatening language',
        'Don\'t click on suspicious links',
        'Verify requests for sensitive information',
        'Look for spelling and grammar errors'
      ]
    },
    {
      title: 'Malware Protection',
      icon: <SecurityIcon />,
      description: 'Understanding different types of malware and prevention methods',
      details: [
        'Keep software and systems updated',
        'Use reliable antivirus software',
        'Avoid downloading from untrusted sources',
        'Scan files before opening',
        'Back up your data regularly'
      ]
    },
    {
      title: 'Social Engineering',
      icon: <SecurityIcon />,
      description: 'Recognizing and preventing social engineering tactics',
      details: [
        'Verify identities before sharing information',
        'Be cautious of unsolicited requests',
        'Don\'t share sensitive information on social media',
        'Use strong authentication methods',
        'Report suspicious activities'
      ]
    },
    {
      title: 'Cryptocurrency Scams',
      icon: <SecurityIcon />,
      description: 'Protecting yourself from cryptocurrency-related fraud',
      details: [
        'Research before investing',
        'Be wary of guaranteed returns',
        'Verify wallet addresses carefully',
        'Don\'t share private keys',
        'Use secure exchanges'
      ]
    },
    {
      title: 'Emerging Threats',
      icon: <SecurityIcon />,
      description: 'Stay informed about new and evolving cyber threats',
      details: [
        'Keep up with security news',
        'Monitor official security advisories',
        'Update security measures regularly',
        'Participate in security awareness training',
        'Follow cybersecurity best practices'
      ]
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom color="white">
        Threat Awareness
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Stay informed about the latest cyber threats and learn how to protect yourself online.
      </Typography>

      <Grid container spacing={3}>
        {threats.map((threat, index) => (
          <Grid item xs={12} key={index}>
            <Card sx={{ bgcolor: 'rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  {React.cloneElement(threat.icon, { 
                    sx: { color: 'primary.main', fontSize: 28 } 
                  })}
                  <Box>
                    <Typography variant="h6" color="white">
                      {threat.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {threat.description}
                    </Typography>
                  </Box>
                </Box>
                <List>
                  {threat.details.map((detail, idx) => (
                    <ListItem key={idx}>
                      <ListItemIcon>
                        <SecurityIcon sx={{ color: 'primary.main' }} />
                      </ListItemIcon>
                      <ListItemText 
                        primary={
                          <Typography color="white">
                            {detail}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default ThreatAwareness;
