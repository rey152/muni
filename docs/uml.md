# Muni data model (UML)

Generated from `pipeline/models.py` by `python3 pipeline/models.py --uml`. Don't edit by hand.

Solid diamonds mean one record contains the other. Dotted arrows mean a field holds the other record's id.

```mermaid
classDiagram
  class Snapshot {
    +str id
    +str url
    +Optional~str~ final_url
    +str fetched_at
    +Optional~str~ checked_on
    +Optional~str~ sha256
    +Optional~str~ content_type
    +Optional~int~ status
    +enum obtained_by
    +enum availability
    +str reason
    +str particular
    +str publisher
    +str title
    +Optional~str~ path
  }
  class Locator {
    +Optional~int~ page
    +Optional~int~ char_start
    +Optional~int~ char_end
    +Optional~str~ element_path
    +str label
  }
  class Role {
    +str code
    +enum method
  }
  class Passage {
    +str id
    +str snapshot_id
    +Locator locator
    +enum kind
    +str text
    +list~Role~ roles
    +str note
  }
  class Authority {
    +str id
    +str name
    +enum tier
  }
  class Topic {
    +str slug
    +str name
    +str description
  }
  class Matter {
    +str id
    +str title
    +list~str~ topics
    +str authority
    +list~str~ authority_ids
    +str location
    +list~int~ wards
    +list~Identifier~ identifiers
    +list~Event~ events
    +list~Condition~ conditions
    +list~ParticipationWindow~ windows
    +list~Claim~ claims
    +list~EasyReadLine~ easy_read
  }
  class Identifier {
    +str value
    +str normalized
    +enum kind
    +str matter_id
    +str passage_id
    +str valid_from
    +str valid_to
    +str note
    +Review review
  }
  class Event {
    +str id
    +str matter_id
    +enum kind
    +str date
    +str actor
    +str outcome_text
    +str passage_id
    +str establishes
    +str not_establishes
    +Review review
  }
  class Condition {
    +str id
    +str matter_id
    +str text
    +str applies_to
    +enum imposed_by
    +str passage_id
    +Review review
  }
  class ParticipationWindow {
    +str id
    +str matter_id
    +str action
    +str channel
    +enum state
    +str deadline_quote
    +Optional~str~ deadline_date
    +str passage_id
    +Optional~str~ checked_on
    +str note
    +Review review
    +Optional~enum~ computed_state
  }
  class Claim {
    +str id
    +str matter_id
    +str section
    +str text
    +enum provenance
    +list~str~ passage_ids
    +str fallback
    +Review review
    +dict checked_against
    +list~str~ qualifiers_required
    +dict qualifiers_waived
  }
  class PlantedClaim {
    +str id
    +str matter_id
    +str section
    +str text
    +enum provenance
    +list~str~ passage_ids
    +str fallback
    +Review review
    +dict checked_against
    +list~str~ qualifiers_required
    +dict qualifiers_waived
    +str note
  }
  class EasyReadLine {
    +str id
    +str matter_id
    +str text
    +str claim_id
    +Optional~float~ grade_level
    +Review review
  }
  class Review {
    +str by
    +Optional~str~ on
    +enum status
    +str note
  }
  class Channel {
    +str id
    +str channel
    +str statement
    +str passage_id
    +Review review
  }
  class RulePair {
    +str id
    +str topic
    +str guide_passage
    +str rule_passage
  }
  class PassageRef {
    +str passage_id
    +str text
  }
  class Discrepancy {
    +str id
    +enum kind
    +str topic
    +Optional~PassageRef~ guide
    +Optional~PassageRef~ rule
    +Optional~str~ claim_id
    +Optional~str~ snapshot_id
    +Optional~str~ checked_sha256
    +Optional~str~ latest_sha256
    +str difference
    +str suggested_fix
    +str found_on
    +enum status
  }
  class Particular {
    +str id
    +str title
    +str level
    +str family
    +str family_name
    +str subfamily
    +str subfamily_name
    +list~str~ components
    +str group
    +str authority
    +str url
    +list~str~ retrieval_urls
    +str access
    +str access_note
    +str pull_confirmed
    +Optional~int~ original_response_status
    +Optional~str~ original_response_kind
    +str publication_structure
    +str transferability
    +str extraction
    +str summary
    +str primary_role
    +str primary_reason
    +list~SecondaryRole~ secondary_roles
    +str role_note
    +str supplied_roles
    +str supplied_primary
    +list~str~ categories
    +str classification_reason
    +str parsing_note
    +str evidence
    +str evidence_detail
    +list~str~ evidence_references
    +list~str~ cross_refs
    +str authority_status
    +list~str~ linked_snapshot_ids
    +list~str~ linked_matter_ids
    +Optional~FetchInfo~ latest_fetch
  }
  class SecondaryRole {
    +str code
    +str reason
  }
  class FetchInfo {
    +str fetched_at
    +str url
    +Optional~str~ final_url
    +Optional~int~ status
    +Optional~enum~ availability
    +str sha256
    +Optional~str~ content_type
    +str obtained_by
    +str path
  }
  class Relationship {
    +str id
    +str categories
    +list~Endpoint~ from
    +list~Endpoint~ to
    +list~list~Endpoint~~ chain
    +list~enum~ arrows
    +list~str~ families
    +str meaning
    +str condition
    +str evidence
    +str url
    +str limitation
    +str connection_basis
    +str dependency
    +str retrieval_dependency
    +str access_context
    +str evidence_url_current_test
    +list~str~ evidence_particular_ids
  }
  class Endpoint {
    +enum kind
    +str value
  }
  class RelationshipFamily {
    +str code
    +str name
    +str verbs
    +str meaning
  }
  class DocumentComponent {
    +str id
    +str label
    +str element_type
    +str description
    +str source_particular
    +str url
    +list~str~ subcategory_codes
  }
  Claim <|-- PlantedClaim
  Channel *-- Review : review
  Channel ..> Passage : passage_id
  Claim *-- Review : review
  Claim ..> Matter : matter_id
  Claim ..> Passage : passage_ids
  Condition *-- Review : review
  Condition ..> Matter : matter_id
  Condition ..> Passage : passage_id
  Discrepancy *-- PassageRef : guide
  Discrepancy *-- PassageRef : rule
  Discrepancy ..> Claim : claim_id
  Discrepancy ..> Snapshot : snapshot_id
  DocumentComponent ..> Particular : source_particular
  EasyReadLine *-- Review : review
  EasyReadLine ..> Claim : claim_id
  EasyReadLine ..> Matter : matter_id
  Event *-- Review : review
  Event ..> Matter : matter_id
  Event ..> Passage : passage_id
  Identifier *-- Review : review
  Identifier ..> Matter : matter_id
  Identifier ..> Passage : passage_id
  Matter *-- Claim : claims
  Matter *-- Condition : conditions
  Matter *-- EasyReadLine : easy_read
  Matter *-- Event : events
  Matter *-- Identifier : identifiers
  Matter *-- ParticipationWindow : windows
  Matter ..> Authority : authority_ids
  ParticipationWindow *-- Review : review
  ParticipationWindow ..> Matter : matter_id
  ParticipationWindow ..> Passage : passage_id
  Particular *-- FetchInfo : latest_fetch
  Particular *-- SecondaryRole : secondary_roles
  Particular ..> Matter : linked_matter_ids
  Particular ..> Particular : cross_refs
  Particular ..> Snapshot : linked_snapshot_ids
  Passage *-- Locator : locator
  Passage *-- Role : roles
  Passage ..> Snapshot : snapshot_id
  PassageRef ..> Passage : passage_id
  PlantedClaim *-- Review : review
  PlantedClaim ..> Matter : matter_id
  PlantedClaim ..> Passage : passage_ids
  Relationship *-- Endpoint : chain
  Relationship *-- Endpoint : from
  Relationship *-- Endpoint : to
  Relationship ..> Particular : evidence_particular_ids
  RulePair ..> Passage : guide_passage
  RulePair ..> Passage : rule_passage
```
