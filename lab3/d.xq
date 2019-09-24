xquery version "3.0";

(: Lab 3 Question d) :)
(: return $city/../name | $city/name :)
<mylist>
  {
  let $d:=doc("mondial.xml")
  let $countries := $d/mondial/country

  let $ctries_and_cties := (
    let $ctrs := (
      for $country in $countries

      let $city := (
        for $city in $country//city

        let $aliases := (
          for $name in $city/name
          return ('&#xa;', <alias>{$name/text()}</alias>)
        )

        return ('&#xa;', <city>{$city/@*[name() = "id"]}{$aliases}&#xa;</city>)
      )

      let $abbr_country := <country name="{$country/name}">{$city}&#xa;</country>
      return ('&#xa;', $abbr_country)
    )
    return $ctrs
  )
  return $ctries_and_cties
  }
</mylist>
