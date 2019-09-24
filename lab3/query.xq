(: let $d:=doc("mondial.xml") :)

(: test :)
(: return $d/mondial/country/name :)

(: Lab 3 Question a) :)
(: for $m in $d/mondial/mountain :)
(: where ($m[@type = "volcano"]) :)
(: return $m/name/text() NOT THIS ONE :)
(: return $m/name :)

(: Lab 3 Question b) :)
(: for $m in $d/mondial/mountain :)
(: where ($m/mountains/text() = "Hawaii") and ($m[@type = "volcano"]) :)
(: return $m/name/text() NOT THIS ONE :)
(: return $m/name :)

(: Lab 3 Question c) Notice that the xs:float conversion is redundant :)
(: for $m in $d/mondial/mountain :)
(: where (xs:float($m/elevation) > xs:float(8000)) :)
(: return $m/name/text() NOT THIS ONE :)
(: return <bigmountain><height>{data($m/elevation)} meters</height><name>{$m/name/text()}</name></bigmountain> :)

(: Lab 3 Question d) :)
(: return $city/../name | $city/name :)
<mylist>
{
let $d:=doc("mondial.xml")
let $countries := $d/mondial/country
let $cities := (
                for $city in $countries/*
                where $city/name
                return $city/../name | $city/name
                )
return element{$countries/name} {''}
}
</mylist>

(: for $city in $cities :)
(: where $city[@country = countries[]] :)

(: <city id="cty-Spain-32" country="E" province="prov-Spain-6"> :)
(: <country car_code="E" ... > :)

(: return $countries/name | $countries/city/@id | $countries/city/name :)
