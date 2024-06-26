Core' 水系核心 |Structure|
=======================================

去中心化应用程序。

  📕 水系核心是骰系去中心化的一种解决方案，提供了强大的 TRPG 规则书处理功能。
  支持在 CLI 中单独使用，同时也提供 REST API 和 WebSocket 通信接口以便其他语言接入。
  此外，它能够读取一种约定式的规则包，并行处理规则包，生成 PDF 文件和本地在线文档站点。

- 🦀 *Rust* 底层实现，“性能优异、速度惊人”。
- 🐍 *Python* 编写的顶层业务逻辑，方便使用、更快入门。
- 📦 兼容的规则包继承解决方案，完善的社区与规则包市场。
- 🛠️ *CLI* 呼出，通过脚手架可以直接使用功能。
- 📃 多语言支持：提供 *REST API* 和 *WebSocket* 接口，支持多语言接入和交互。
- 🏗️ 并行处理，使用 *Rust* 实现的规则包加载模块支持并行处理，提高性能。
- 📚 *PDF* 生成，结合自定义 *PDF* 模板，能够生成符合需求的 *PDF* 书籍。
- 🌏 离线文档与在线协作站点，使用 *Sphinx* 框架与 *Vue* 技术栈生成本地文档与在线站点。


..
  架构设计
  -------
  
  .. code-block:: mermaid
  
    graph TD;
      A-->B;
      A-->C;
      B-->D;
      C-->D;
  
  
  .. code-block:: stl
  
    solid cube_corner
      facet normal 0.0 -1.0 0.0
        outer loop
          vertex 0.0 0.0 0.0
          vertex 1.0 0.0 0.0
          vertex 0.0 0.0 1.0
        endloop
      endfacet
      facet normal 0.0 0.0 -1.0
        outer loop
          vertex 0.0 0.0 0.0
          vertex 0.0 1.0 0.0
          vertex 1.0 0.0 0.0
        endloop
      endfacet
      facet normal -1.0 0.0 0.0
        outer loop
          vertex 0.0 0.0 0.0
          vertex 0.0 0.0 1.0
          vertex 0.0 1.0 0.0
        endloop
      endfacet
      facet normal 0.577 0.577 0.577
        outer loop
          vertex 1.0 0.0 0.0
          vertex 0.0 1.0 0.0
          vertex 0.0 0.0 1.0
        endloop
      endfacet
    endsolid


----

`AGPL3.0`_ © 2023-PRESENT `简律纯`_ & `HydroRoll-Team`_.

|license icon|

|FOSSA Status|



.. uri list above:
.. _AGPL3.0: https://github.com/HydroRoll-Team/HydroRollCore/blob/main/LICENSE
.. _简律纯: https://github.com/HsiangNianian
.. _HydroRoll-Team: https://github.com/HydroRoll-Team

.. image list above:
.. |Structure| image:: https://images.repography.com/39938419/HydroRoll-Team/HydroRollCore/structure/tMt9z2RexIQ8rnXCIMFWe7YTZtx9reheQCtxqgPqZ1Q/XERnotqf4h5EPFL215lPSb7Dk3fQ5EUniRD-gEckW3M_table.svg
   :alt: Structure
   :target: https://github.com/HydroRoll-Team/HydroRollCore
   :width: 60

.. image list above:
.. |license icon| image:: https://app.fossa.com/api/projects/git%2Bgithub.com%2FHydroRoll-Team%2FHydroRollCore.svg?type=shield&issueType=license
   :target: https://app.fossa.com/projects/git%2Bgithub.com%2FHydroRoll-Team%2FHydroRollCore?ref=badge_shield&issueType=license
.. |FOSSA Status| image:: https://app.fossa.com/api/projects/git%2Bgithub.com%2FHydroRoll-Team%2FHydroRollCore.svg?type=large&issueType=license
   :target: https://app.fossa.com/projects/git%2Bgithub.com%2FHydroRoll-Team%2FHydroRollCore?ref=badge_large&issueType=license
