```
[
    <<gd.loop|100|,>>
    {
        "name": "<<gd.name.findName>>",
        "id": "<<gd.random.uuid>>",
        "phone": "<<gd.phone.phoneNumber>>",
        "address": [
        <<gd.loop|2|,>>
            {
                "street": "<<gd.address.streetName>>",
                "number": <<gd.random.number>>,
                "secondaryAddress": "<<gd.address.secondaryAddress>>",
                "county": "<<gd.address.county>>",
                "city": "<<gd.address.city>>",
                "zipCode": "<<gd.address.zipCode>>",
                "state": "<<gd.address.state>>",
                "country": "<<gd.address.country>>"
            }
        <</gd.loop>>
        ]
    }
    <</gd.loop>>
]
```