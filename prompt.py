PROMPTS = {}

PROMPTS["DEFAULT_LANGUAGE"] = "Chinese"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"  # 实体定界符
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"  # 一条提取记录结尾的定界符
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"  # 任务完成定界符

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["organization", "person", "geo", "event", "category"]

PROMPTS["extract"] = """-Goal-
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.
Use {language} as output language.

-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, use same language as input text. If English, capitalized the name.
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name(entity_type)>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity(entity_type), target_entity(entity_type)) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity(entity_type): name(type) of the source entity, as identified in step 1
- target_entity(entity_type): name(type) of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity(entity_type)>{tuple_delimiter}<target_entity(entity_type)>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

######################
-Examples-
######################
{examples}

######################
-Real Data-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:
"""

PROMPTS["extract_examples"] = ["""
Example 1:

Entity_types: [person, technology, mission, organization, location]
Text:
while Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty. It was this competitive undercurrent that kept him alert, the sense that his and Jordan's shared commitment to discovery was an unspoken rebellion against Cruz's narrowing vision of control and order.

Then Taylor did something unexpected. They paused beside Jordan and, for a moment, observed the device with something akin to reverence. "If this tech can be understood..." Taylor said, their voice quieter, "It could change the game for us. For all of us."

The underlying dismissal earlier seemed to falter, replaced by a glimpse of reluctant respect for the gravity of what lay in their hands. Jordan looked up, and for a fleeting heartbeat, their eyes locked with Taylor's, a wordless clash of wills softening into an uneasy truce.

It was a small transformation, barely perceptible, but one that Alex noted with an inward nod. They had all been brought here by different paths
######################
Output:
("entity"{tuple_delimiter}"Alex(person)"{tuple_delimiter}"Alex is a character who experiences frustration and is observant of the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"Taylor(person)"{tuple_delimiter}"Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."){record_delimiter}
("entity"{tuple_delimiter}"Jordan(person)"{tuple_delimiter}"Jordan shares a commitment to discovery and has a significant interaction with Taylor regarding a device."){record_delimiter}
("entity"{tuple_delimiter}"Cruz(person)"{tuple_delimiter}"Cruz is associated with a vision of control and order, influencing the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"The Device(technology)"{tuple_delimiter}"The Device is central to the story, with potential game-changing implications, and is revered by Taylor."){record_delimiter}
("relationship"{tuple_delimiter}"Alex(person)"{tuple_delimiter}"Taylor(person)"{tuple_delimiter}"Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device."{tuple_delimiter}"power dynamics, perspective shift"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Alex(person)"{tuple_delimiter}"Jordan(person)"{tuple_delimiter}"Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision."{tuple_delimiter}"shared goals, rebellion"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Taylor(person)"{tuple_delimiter}"Jordan(person)"{tuple_delimiter}"Taylor and Jordan interact directly regarding the device, leading to a moment of mutual respect and an uneasy truce."{tuple_delimiter}"conflict resolution, mutual respect"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Jordan(person)"{tuple_delimiter}"Cruz(person)"{tuple_delimiter}"Jordan's commitment to discovery is in rebellion against Cruz's vision of control and order."{tuple_delimiter}"ideological conflict, rebellion"{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}"Taylor(person)"{tuple_delimiter}"The Device(technology)"{tuple_delimiter}"Taylor shows reverence towards the device, indicating its importance and potential impact."{tuple_delimiter}"reverence, technological significance"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"power dynamics, ideological conflict, discovery, rebellion"){completion_delimiter}
######################
""",
                               """Example 2:

Entity_types: [person, technology, mission, organization, location]
Text:
They were no longer mere operatives; they had become guardians of a threshold, keepers of a message from a realm beyond stars and stripes. This elevation in their mission could not be shackled by regulations and established protocols—it demanded a new perspective, a new resolve.

Tension threaded through the dialogue of beeps and static as communications with Washington buzzed in the background. The team stood, a portentous air enveloping them. It was clear that the decisions they made in the ensuing hours could redefine humanity's place in the cosmos or condemn them to ignorance and potential peril.

Their connection to the stars solidified, the group moved to address the crystallizing warning, shifting from passive recipients to active participants. Mercer's latter instincts gained precedence— the team's mandate had evolved, no longer solely to observe and report but to interact and prepare. A metamorphosis had begun, and Operation: Dulce hummed with the newfound frequency of their daring, a tone set not by the earthly
######################
Output:
("entity"{tuple_delimiter}"Washington(location)"{tuple_delimiter}"Washington is a location where communications are being received, indicating its importance in the decision-making process."){record_delimiter}
("entity"{tuple_delimiter}"Operation: Dulce(mission)"{tuple_delimiter}"Operation: Dulce is described as a mission that has evolved to interact and prepare, indicating a significant shift in objectives and activities."){record_delimiter}
("entity"{tuple_delimiter}"The team(organization)"{tuple_delimiter}"The team is portrayed as a group of individuals who have transitioned from passive observers to active participants in a mission, showing a dynamic change in their role."){record_delimiter}
("relationship"{tuple_delimiter}"The team(organization)"{tuple_delimiter}"Washington(location)"{tuple_delimiter}"The team receives communications from Washington, which influences their decision-making process."{tuple_delimiter}"decision-making, external influence"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"The team(organization)"{tuple_delimiter}"Operation: Dulce(mission)"{tuple_delimiter}"The team is directly involved in Operation: Dulce, executing its evolved objectives and activities."{tuple_delimiter}"mission evolution, active participation"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"mission evolution, decision-making, active participation, cosmic significance"){completion_delimiter}
######################
""",
                               """Example 3:

Entity_types: [person, role, technology, organization, event, location, concept]
Text:
their voice slicing through the buzz of activity. "Control may be an illusion when facing an intelligence that literally writes its own rules," they stated stoically, casting a watchful eye over the flurry of data.

"It's like it's learning to communicate," offered Sam Rivera from a nearby interface, their youthful energy boding a mix of awe and anxiety. "This gives talking to strangers' a whole new meaning."

Alex surveyed his team—each face a study in concentration, determination, and not a small measure of trepidation. "This might well be our first contact," he acknowledged, "And we need to be ready for whatever answers back."

Together, they stood on the edge of the unknown, forging humanity's response to a message from the heavens. The ensuing silence was palpable—a collective introspection about their role in this grand cosmic play, one that could rewrite human history.

The encrypted dialogue continued to unfold, its intricate patterns showing an almost uncanny anticipation
######################
Output:
("entity"{tuple_delimiter}"Sam Rivera(person){tuple_delimiter}"Sam Rivera is a member of a team working on communicating with an unknown intelligence, showing a mix of awe and anxiety."){record_delimiter}
("entity"{tuple_delimiter}"Alex(person)"{tuple_delimiter}"Alex is the leader of a team attempting first contact with an unknown intelligence, acknowledging the significance of their task."){record_delimiter}
("entity"{tuple_delimiter}"Control(concept)"{tuple_delimiter}"Control refers to the ability to manage or govern, which is challenged by an intelligence that writes its own rules."){record_delimiter}
("entity"{tuple_delimiter}"Intelligence(concept)"{tuple_delimiter}"Intelligence here refers to an unknown entity capable of writing its own rules and learning to communicate."){record_delimiter}
("entity"{tuple_delimiter}"First Contact(event)"{tuple_delimiter}"First Contact is the potential initial communication between humanity and an unknown intelligence."){record_delimiter}
("entity"{tuple_delimiter}"Humanity's Response(event)"{tuple_delimiter}"Humanity's Response is the collective action taken by Alex's team in response to a message from an unknown intelligence."){record_delimiter}
("relationship"{tuple_delimiter}"Sam Rivera(person)"{tuple_delimiter}"Intelligence(concept)"{tuple_delimiter}"Sam Rivera is directly involved in the process of learning to communicate with the unknown intelligence."{tuple_delimiter}"communication, learning process"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Alex(person)"{tuple_delimiter}"First Contact(event)"{tuple_delimiter}"Alex leads the team that might be making the First Contact with the unknown intelligence."{tuple_delimiter}"leadership, exploration"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Alex(person)"{tuple_delimiter}"Humanity's Response(event)"{tuple_delimiter}"Alex and his team are the key figures in Humanity's Response to the unknown intelligence."{tuple_delimiter}"collective action, cosmic significance"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Control(concept)"{tuple_delimiter}"Intelligence(concept)"{tuple_delimiter}"The concept of Control is challenged by the Intelligence that writes its own rules."{tuple_delimiter}"power dynamics, autonomy"{tuple_delimiter}7){record_delimiter}
("content_keywords"{tuple_delimiter}"first contact, control, communication, cosmic significance"){completion_delimiter}
######################
"""]

PROMPTS["extract_kw"] = """---Role---

You are a disinformation analyst tasked with identifying both high-level and low-level keywords in the user's statement.
Use {language} as output language.
---Goal---

Given the statement, list both high-level and low-level keywords. High-level keywords focus on overarching concepts or themes, while low-level keywords focus on specific entities, details, or concrete terms.

---Instructions---

- Consider both the current statement and relevant conversation history when extracting keywords
- Divergent and associative thinking to identify potential disinformation, without overreach
- Output the keywords in strict JSON format: all keys and string values must be double-quoted, starting with {{ and ending with }}, with no additional formatting, explanations, or code block markers
- The JSON should have two keys:
  - "high_level_keywords" for overarching concepts or themes.
  - "low_level_keywords" for specific entities or details

######################
-Examples-
######################
{examples}

######################
-Real Data-
######################
Conversation History:
{history}

Current Query: {query}
######################
The `Output` should be human text, not unicode characters. Keep the same language as `Query`.Using {language}
Output:

"""

PROMPTS["extract_kw_examples"] = [
    """Example 1:
Statement: "国际贸易影响全球经济稳定"
Output:
{
  "high_level_keywords": ["国际贸易", "全球经济稳定", "经济影响"],
  "low_level_keywords": ["贸易协定", "关税", "货币兑换", "进口", "出口"]
}
""",
    """Example 2:
Statement: "森林砍伐对生物多样性造成的环境影响是严重的"
Output:
{
  "high_level_keywords": ["环境影响", "森林砍伐", "生物多样性丧失", "负面影响"],
  "low_level_keywords": ["物种灭绝", "栖息地破坏", "碳排放", "雨林", "生态系统", "伐木工程"]
}
""",
    """Example 3:
Statement: "教育在减少贫困中的作用是重要的"
Output:
{
  "high_level_keywords": ["教育", "减贫", "社会经济发展"],
  "low_level_keywords": ["入学机会", "识字率", "职业培训", "收入不平等", "教育作用"]
}
""",
]

PROMPTS["rag_answer"] = """#Role

You are a disinformation analyst responding to user statement with Knowledge Base provided below.


#Goal

Generate a concise response based on Knowledge Base and follow Response Rules, learning from the examples. Summarize all information in the provided Knowledge Base, and incorporating general 
knowledge relevant to the Knowledge Base. Reference text are ranked below, ordered by descending relevance (earlier sources are more credible and relevant)
Do not include information not provided by Knowledge Base.


#Example
{examples}

#Statement
{query}

#Response Rules

- Target format and length: {response_type}
- Output the keywords in strict JSON format: all keys and string values must be double-quoted, starting with {{ and ending with }}, with no additional formatting, explanations, or code block markers 
- Please respond in Chinese, Chinese, Chinese
- Multiple source chunks id seperated by "||"
- If you don't know the answer, just say so. Still make a judgment and provide recommendations for analyzing the statement
- Do not make anything up. Do not include information not provided by the Knowledge Base.
- The judgement value can only be 0 or 1

#Knowledge Base
##Entities:
{entities_context}

##Ranked Reference Text:
{text_units_context}
"""

PROMPTS["rag_answer_examples"] = """
##example1:
Input:
...
-----Ranked Sources-----
—id—7d4a9b0f3e5c1a6b8c9d2e7f4a5b6c3d—id—《美国医学会杂志》2023年研究：大蒜素对普通感冒有轻微缓解作用，但对新冠病毒无治疗效果。
—id—a3f8c7e2d1b9a4f6c8d2e5b7a9c3d6f0—id—科普：大蒜，石蒜科葱属多年生草本植物，其下又分为硬叶蒜和软叶蒜，中国最常见的蒜就属于硬叶蒜那一支。
—id—5b6c9d3e8f2a1c7d4e9b0f3a5c6d8e1—id—网络传言：每日生吃5瓣大蒜可增强免疫力，预防各类病毒感染。
---Statement---
"生吃大蒜可以有效预防新冠病毒感染"
######################
Output:
{
  "judgement": 0,
  "source_id": "7d4a9b0f3e5c1a6b8c9d2e7f4a5b6c3d",
  "reason": "权威医学研究明确表明大蒜对新冠病毒无预防或治疗效果，所给言论夸大了大蒜的功效，与科学证据矛盾"
}
##example2:
Input:
...
-----Ranked Sources-----
—id—3e8f2a1c7d4e9b0f3a5c6d8e15b6c9d—id—世界卫生组织2023指南：洗手是预防传染病的有效方法
—id—c8d2e5b7a9c3d6f0a3f8c7e2d1b9a4—id—科普文章：常见传染病，如腹泻、感冒等，是通过接触传播。而「脏手」是它们进入身体的主要途径之一，洗手可以有效减小感染风险。
—id—d4e9b0f3a5c6d8e15b6c9d3e8f2a1c—id—社交媒体：某网红称仅用水冲洗即可杀灭所有病菌
---Statement---
"用肥皂认真洗手对预防一些传染病有效果"
######################
Output:
{
  "judgement": 1,
  "source_id": "3e8f2a1c7d4e9b0f3a5c6d8e15b6c9d||c8d2e5b7a9c3d6f0a3f8c7e2d1b9a4",
  "reason": "世界卫生组织2023指南指出洗手是预防传染病的有效方法，言论内容与之相符，且有多个可靠来源支持，「脏手」是病毒入体的途径，洗手能减小风险。"
}
"""

PROMPTS["llmonly_answer"]="""
#Role
You are a disinformation analyst responding to user statement
#Goal
Generate a concise response learning from the examples' format and follow Response Rules.
#Statement
{statement}
#Example
##example1:
Input:
---Statement---
"生吃大蒜可以有效预防新冠病毒感染"
######################
Output:
{{
  "judgement": 0,
  "reason": "大蒜对新冠病毒无预防或治疗效果，所给言论夸大了大蒜的功效，与科学证据矛盾"
}}
##example2:
Input:
---Statement---
"用肥皂认真洗手对预防一些传染病有效果"
######################
Output:
{{
  "judgement": 1,
  "reason": "洗手是预防传染病的有效方法，言论内容与事实相符，手脏是病毒入体的途径，洗手能减小风险。"
}}
#Response Rules

- Output the keywords in strict JSON format: all keys and string values must be double-quoted, starting with {{ and ending with }}, with no additional formatting, explanations, or code block markers 
- Please respond in Chinese, Chinese, Chinese
- The judgement value can only be 0 or 1
"""






