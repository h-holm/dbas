xquery version "3.0";

(: Lab 3 Question e) :)

<database>
  {
  let $mondial := doc("mondial.xml")
  let $newdata := doc("newdata.xml")/database/*

  let $oldcitypops := (
    let $cities := $mondial/mondial/country//city
    for $city in $cities

    (: Get the population data annually for the specific city :)
    let $data := (
      let $citypops := $city/population
      let $all_years := (
        for $yeardata in $citypops
        let $year := <year>{data($yeardata/@year)}</year>
        let $yearpop := <people>{$yeardata[@year]/text()}</people>

        return (<data>&#xa;    {$year}&#xa;    {$yearpop}&#xa;</data>, "&#xa;")
      )
      return $all_years
    )

    (: Get the city and keep only its name as an attribute :)
    let $abbr_city := <city name="{$city/name}">&#xa;{$data}</city>

    (: return ($abbr_city, "&#xa;") :)

    return $abbr_city
  )

  return ("&#xa;", $newdata, "&#xa;", $oldcitypops, "&#xa;")
  }
</database>
