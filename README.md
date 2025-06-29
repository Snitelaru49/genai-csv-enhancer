# GenAI CSV Enhancer

A powerful Streamlit application that uses Amazon Bedrock AI to intelligently generate new rows for your CSV datasets.

## 🚀 Features

- **CSV Upload & Analysis**: Upload datasets and get comprehensive schema analysis
- **AI-Powered Generation**: Uses Claude 3 Sonnet via AWS Bedrock to generate realistic new rows
- **Interactive Editing**: Review and modify generated rows before export
- **Bias Detection**: Automatically flags potential biases in generated data
- **Visual Analytics**: Compare before/after data distributions
- **Flexible Regeneration**: Generate with different data samples
- **One-Click Export**: Download enhanced datasets as CSV

## 🛠️ Setup Instructions

### Prerequisites

1. **AWS Account** with Bedrock access
2. **Python 3.8+**
3. **AWS CLI configured** or environment variables set

### Local Development Setup

1. **Clone and navigate to the project**:
   ```bash
   cd "e:\Projects\GENAI hackathon"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials** (choose one):
   
   **Option A: AWS CLI**
   ```bash
   aws configure
   ```
   
   **Option B: Environment Variables**
   ```bash
   set AWS_ACCESS_KEY_ID=your_access_key
   set AWS_SECRET_ACCESS_KEY=your_secret_key
   set AWS_DEFAULT_REGION=us-east-1
   ```
   
   **Option C: IAM Role** (recommended for EC2)

4. **Ensure Bedrock Model Access**:
   - Go to AWS Bedrock Console
   - Navigate to "Model access"
   - Request access for Claude 3 Sonnet
   - Wait for approval (usually instant)

5. **Run the application**:
   ```bash
   streamlit run main.py
   ```

### AWS Cloud Deployment

#### Option 1: EC2 Deployment

1. **Launch EC2 Instance**:
   - Amazon Linux 2 or Ubuntu 20.04+
   - t3.medium or larger (for better performance)
   - Attach IAM role with Bedrock permissions

2. **Install dependencies**:
   ```bash
   sudo yum update -y  # For Amazon Linux
   sudo yum install -y python3 python3-pip git
   
   # Clone your repository
   git clone <your-repo-url>
   cd genai-csv-enhancer
   
   # Install Python packages
   pip3 install -r requirements.txt
   ```

3. **Run with port forwarding**:
   ```bash
   streamlit run main.py --server.port 8501 --server.address 0.0.0.0
   ```

4. **Access via browser**:
   ```
   http://your-ec2-public-ip:8501
   ```

#### Option 2: Lambda + S3 (Advanced)

For serverless deployment, you can package the app using AWS Lambda with container images.

### IAM Permissions Required

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels",
                "bedrock:GetFoundationModel"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🎯 Usage Guide

1. **Upload CSV**: Click "Choose your CSV file" and select your dataset
2. **Review Analysis**: Check schema, sample data, and distributions
3. **Configure Generation**: Use sidebar to set number of rows and options
4. **Generate Rows**: Click "Generate New Rows" to create AI-generated data
5. **Review & Edit**: Modify generated rows in the interactive table
6. **Check for Bias**: Review bias analysis warnings
7. **Export**: Preview and download your enhanced dataset

## 🔧 Configuration

Edit `config.py` to customize:

- **AWS_REGION**: Your preferred AWS region
- **BEDROCK_MODEL_ID**: Claude model to use
- **MAX_FILE_SIZE_MB**: Maximum upload size
- **DEFAULT_SUGGESTED_ROWS**: Default number of rows to generate

## 📊 Supported Data Types

- **Numeric**: Integers, floats, decimals
- **Categorical**: Strings, categories, labels
- **Mixed**: Datasets with various column types

## 🔐 Security Considerations

- AWS credentials are never stored in the application
- CSV files are processed in memory only
- Generated data follows privacy-preserving patterns
- No data is sent to external services besides AWS Bedrock

## 🐛 Troubleshooting

### Common Issues

1. **"Bedrock client not available"**:
   - Check AWS credentials configuration
   - Verify region has Bedrock access
   - Ensure model permissions are granted

2. **"Import pandas could not be resolved"**:
   - Install dependencies: `pip install -r requirements.txt`

3. **"Error generating rows"**:
   - Check your CSV has proper headers
   - Ensure at least 2-3 rows of sample data
   - Verify internet connectivity for Bedrock API

### Performance Tips

- For large datasets (>1000 rows), consider sampling
- Use fewer columns for faster generation
- Start with smaller row counts (5-10) for testing

## 📈 Cost Estimation

AWS Bedrock costs approximately:
- Claude 3 Sonnet: ~$0.003 per 1000 input tokens
- Typical generation: 500-1500 tokens per request
- Cost per generation: ~$0.002-0.005

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review AWS Bedrock documentation
3. Create an issue in the repository
