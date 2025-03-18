export const PLACEHOLDER_WORKSPACE = [
  {
    id: '12345678-1234-1234-1234-123456789012',
    name: 'john-doe',
    account: '87654321-4321-4321-4321-210987654321',
    member_group: 'john-doe',
    status: 'Ready',
    stores: [
      {
        object: [
          {
            store_id: 'abcdefab-abcd-abcd-abcd-abcdefabcdef',
            name: 'john-doe',
            bucket: 'workspaces-example-staging',
            prefix: 'john-doe/',
            host: 'example-staging-vancrslr-john-doe-s3-123456789012.s3-accesspoint.eu-west-2.amazonaws.com',
            env_var: 'S3_BUCKET_WORKSPACE',
            access_point_arn:
              'arn:aws:s3:eu-west-2:123456789012:accesspoint/example-staging-vancrslr-john-doe-s3',
            access_url:
              'https://john-doe.staging.example-workspaces.org.uk/files/workspaces-example-staging/',
          },
        ],
        block: [
          {
            store_id: 'fedcbafe-dcba-dcba-dcba-fedcbafedcba',
            name: 'john-doe',
            access_point_id: 'fsap-1234567890abcdef',
            mount_point: '/workspaces/john-doe',
          },
        ],
      },
    ],
    last_updated: '2025-02-12T13:35:31.960167Z',
  },
];
