# IAM Policies

The skill performs only the BSS `ListSubCustomerCoupons` read operation.

## Least-Privilege Policy

Use the following read-only action pattern, subject to the account's available
IAM actions and site configuration:

```json
{
  "Version": "5.0",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bss:*:get",
        "bss:*:list"
      ],
      "Resource": ["*"]
    }
  ]
}
```

Do not grant BSS write, payment, transfer, refund, renewal, unsubscribe, or
coupon-claim actions. If the IAM console requires an explicit action name,
select only the read action corresponding to `ListSubCustomerCoupons`.

The account must be able to access this operation. A regular account that
cannot access the BSS coupon list must not be broadened to partner permissions.
