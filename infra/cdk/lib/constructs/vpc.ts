import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export interface VpcConstructProps {
    maxAzs?: number;
    cidr?: string;
}

export class VpcConstruct extends Construct {
    public readonly vpc: ec2.Vpc;
    public readonly privateSubnets: ec2.ISubnet[];
    public readonly publicSubnets: ec2.ISubnet[];

    constructor(scope: Construct, id: string, props?: VpcConstructProps) {
        super(scope, id);

        this.vpc = new ec2.Vpc(this, 'ApiVerseVpc', {
            maxAzs: props?.maxAzs || 2,
            cidr: props?.cidr || '10.0.0.0/16',

            subnetConfiguration: [
                {
                    name: 'Public',
                    subnetType: ec2.SubnetType.PUBLIC,
                    cidrMask: 24,
                },
                {
                    name: 'Private',
                    subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidrMask: 24,
                },
            ],

            natGatewayProvider: ec2.NatProvider.instanceV2({
                instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
            }),
            natGateways: 1,
            enableDnsHostnames: true,
            enableDnsSupport: true,
        });

        this.privateSubnets = this.vpc.privateSubnets;
        this.publicSubnets = this.vpc.publicSubnets;

        cdk.Tags.of(this.vpc).add('Name', 'ApiVerse-VPC');
        cdk.Tags.of(this.vpc).add('Project', 'ApiVerse');

        this.vpc.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY);
    }
}