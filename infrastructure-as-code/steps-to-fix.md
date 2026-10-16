# Add steps/actions here:

Terraform 'count' uses indexes sequentially from 0 to n-1, 0-4 in this case for 5 resources. Removing index [1] would affect other resources as count variable is part of the resource naming convention. To delete 2nd resource without impacting other resources I would use for_each in combination with terraform state mv instead of count [1] [2]. 

1. step 1: Changing from 'count' to 'for_each'
Firstly retaining all five keys, names for the resources
```hcl
#Before
count =5
name = server-$(count.index + 1)

#After (for_each with a static mapping)
for_each = toset(["0", "1", "2", "3", "4"])
name = server-${tonumber(each.key) + 1}"
```
2. step 2: Moving existing state addresses
   ```bash
   for x in 0 1 2 3 4; do
   terraform state mv "server-[x]" "server-[x]"
   done
   ```

4. Step 3: Removing 2nd resource
   ```hcl
   for_each = toset(["0", "2", "3", "4"])
   ```
   ```bash
   terraform apply delete.terraformplan
   ```

   5. Step 5: Verify
      ```bash
      terraform plan
      terraform apply
      ```
      Should show, "No changes"

References:
[1] for_each reference - https://developer.hashicorp.com/terraform/language/meta-arguments/for_each
[2] terraform state mv command - https://developer.hashicorp.com/terraform/cli/commands/state/mv
