import * as cdk from 'aws-cdk-lib';
import * as events from 'aws-cdk-lib/aws-events';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export interface WebhooksConstructProps {
    lambdaFunction: lambda.IFunction;
}

export class WebhooksConstruct extends Construct {
    public readonly eventBus: events.EventBus;
    public readonly webhookQueue: sqs.Queue;
    public readonly deadLetterQueue: sqs.Queue;

    constructor(scope: Construct, id: string, props: WebhooksConstructProps) {
        super(scope, id);

        this.deadLetterQueue = new sqs.Queue(this, 'WebhookDLQ', {
            queueName: 'apiverse-webhook-dlq',
            retentionPeriod: cdk.Duration.days(14),
            removalPolicy: cdk.RemovalPolicy.DESTROY,
        });

        this.webhookQueue = new sqs.Queue(this, 'WebhookQueue', {
            queueName: 'apiverse-webhook-queue',
            visibilityTimeout: cdk.Duration.seconds(300),
            retentionPeriod: cdk.Duration.days(7),

            deadLetterQueue: {
                queue: this.deadLetterQueue,
                maxReceiveCount: 3, 
            },
            
            removalPolicy: cdk.RemovalPolicy.DESTROY,
        });

        this.eventBus = new events.EventBus(this, 'WebhookEventBus', {
            eventBusName: 'apiverse-webhooks',
        });

        new events.Rule(this, 'WebhookRule', {
            eventBus: this.eventBus,
            eventPattern: {
                source: ['apiverse'],
                detailType: [
                    'schema_change',
                    'rate_limit_exceeded',
                    'api_down',
                    'usage_threshold',
                ],
            },
            targets: [new targets.SqsQueue(this.webhookQueue)],
        });

        props.lambdaFunction.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: ['events:PutEvents'],
            resources: [this.eventBus.eventBusArn],
        }));

        this.webhookQueue.grantSendMessages(props.lambdaFunction);

        cdk.Tags.of(this.eventBus).add('Name', 'ApiVerse-EventBus');
        cdk.Tags.of(this.eventBus).add('Project', 'ApiVerse');
        cdk.Tags.of(this.webhookQueue).add('Name', 'ApiVerse-Webhook-Queue');
        cdk.Tags.of(this.webhookQueue).add('Project', 'ApiVerse');

        this.eventBus.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY);
    }

    public getEventBusName(): string {
        return this.eventBus.eventBusName;
    }

    public getQueueUrl(): string {
        return this.webhookQueue.queueUrl;
    }

    public getQueueArn(): string {
        return this.webhookQueue.queueArn;
    }
}
