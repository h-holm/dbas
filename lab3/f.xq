xquery version "3.0";

(: Lab 3 Question e) :)
(: return $city/../name | $city/name :)
<manycities>
  {
  let $mondial := doc("mondial.xml")
  let $newdata := doc("newdata.xml")
  let $cities := $mondial/mondial/country//city


  for $city in $cities

  (: Get the city and keep only its name as an attribute :)
  let $abbr_city := <city name="{$city/name}">&#xa;</city>

  (: Get the population data annually for the specific city :)
  let $data := (
    let $citypops := $city/population
    let $all_years := (
      for $yeardata in $citypops
      let $year := $yeardata[@year]/text()
      return $year
    )
  )

  return $citypops
  (: return ($abbr_city, "&#xa;") :)
  }
</manycities>
