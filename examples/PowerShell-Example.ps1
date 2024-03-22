<#
    Example on how create new Azure Virtual Network Subnet using the Get-AzVirutalNetwork function
#>

#region variables
$virtualNetworkResourceGroupName = 'demo-vnet-rg'
$virtualNetworkName = 'demo-vnet'
$subnetIpAddresses = 3
#endregion

Function Get-AzVirtualNetworkRange {
    <#
    .SYNOPSIS
    This script is an example of how to use the API to get the available IP addresses in a VNET and Subnet.
    
    .DESCRIPTION
    This script is an example of how to use the API to get the available IP addresses in a VNET and Subnet.
    
    .PARAMETER VnetIpRange
    The IP range of the VNET.
    
    .PARAMETER SubnetIpRange
    The IP range of the Subnet.
    
    .PARAMETER requiredIp
    The IP address that you want to check if it is available.
    
    .EXAMPLE
    Get-AzVirtualNetwork -Name 'databricks-vnet' -ResourceGroupName 'databricks-vnet-rg' | select-object -Property @{'L'='VnetIPrange';'E'={($_.AddressSpaceText | 
        ConvertFrom-Json).AddressPrefixes}}, @{'L'='SubnetIpRange';'E'={(($_.SubnetsText | 
            ConvertFrom-Json).AddressPrefix) -join ','}} | 
                Get-AzVirtualNetworkRange -requiredIp 10
    #>
        
    [CmdLetBinding()]
    Param (
        [Parameter (Mandatory = $true, ValueFromPipelineByPropertyName = $true)]
        [String] $VnetIpRange,
    
        [Parameter (Mandatory = $true, ValueFromPipelineByPropertyName = $true)]
        [String]$SubnetIpRange,
    
        [Parameter (Mandatory = $true)]
        [int] $requiredIp
    )
    
    $headers = @{}
    $headers.Add("Content-Type", "multipart/form-data")
    $contentType = 'multipart/form-data; boundary=kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A'
    
    $reqUrl = 'https://azure-subnet-copilot.vercel.app/'
    $body = @"
--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A
Content-Disposition: form-data; name="vnet_iprange"

$VnetIpRange
--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A
Content-Disposition: form-data; name="subnet_ipranges"

$SubnetIpRange
--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A
Content-Disposition: form-data; name="required_ips"

$requiredIp
--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A
Content-Disposition: form-data; name="json_output"

on
--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A--
"@

    $invokeRestMethodSplat = @{
        Uri         = $reqUrl
        Method      = 'Post'
        Headers     = $headers
        ContentType = $contentType
        Body        = $body
    }
    Invoke-RestMethod @invokeRestMethodSplat
}

#region get virtual network
$virtualNetwork = Get-AzVirtualNetwork -ResourceGroupName $virtualNetworkResourceGroupName -Name $virtualNetworkName
#endregion

#region get suitable subnet ip range
$virtualNetwork | select-object -Property @{'L' = 'VnetIPrange'; 'E' = { ($_.AddressSpaceText | ConvertFrom-Json).AddressPrefixes } }, @{'L' = 'SubnetIpRange'; 'E' = { (($_.SubnetsText | ConvertFrom-Json).AddressPrefix) -join ',' } } |  
Get-AzVirtualNetworkRange -requiredIp $subnetIpAddresses -OutVariable suitableSubnet
$suitableSubnet
#endregion

#region create new subnet with random name
$randomName = -join ((65..90) + (97..122) | Get-Random -Count 8 | ForEach-Object { [char]$_ })
$subnet = @{    
    name           = ('subnet-{0}' -f $randomName)
    VirtualNetwork = $virtualNetwork
    AddressPrefix  = $($suitableSubnet.suitable_ip_range)
}
Add-AzVirtualNetworkSubnetConfig @subnet
$virtualNetwork | Set-AzVirtualNetwork
#endregion