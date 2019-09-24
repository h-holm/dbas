xquery version "3.0";

(: Lab 3 Question e) :)
(: return $city/../name | $city/name :)
<manycities>
  {
  let $d:=doc("mondial.xml")
  let $countries := $d/mondial/country

  let $over40s := (
    for $country in $countries
    where count($country//city) > 40
    return if (count($country//city) > 60)
           then <country note="morethan60" name="{$country/name}">{count($country//city)}</country>
           else <country name="{$country/name}">{count($country//city)}</country>
  )

  return $over40s
  }
</manycities>
