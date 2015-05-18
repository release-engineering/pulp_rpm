import os

from pulp.plugins.util.metadata_writer import FastForwardXmlFileContext
from pulp_rpm.plugins.importers.yum.parse import rpm as rpm_parse

from pulp_rpm.plugins.distributors.yum.metadata.metadata import REPO_DATA_DIR_NAME
from pulp_rpm.yum_plugin import util


_LOG = util.getLogger(__name__)

PRIMARY_XML_FILE_NAME = 'primary.xml.gz'
COMMON_NAMESPACE = 'http://linux.duke.edu/metadata/common'
RPM_NAMESPACE = 'http://linux.duke.edu/metadata/rpm'


class PrimaryXMLFileContext(FastForwardXmlFileContext):
    """
    Context manager for generating the primary.xml.gz metadata file.
    """

    def __init__(self, working_dir, num_units, checksum_type=None):
        """
        :param working_dir: working directory to create the primary.xml.gz in
        :type  working_dir: str
        :param num_units: total number of units whose metadata will be written
                          into the primary.xml.gz metadata file, or the number of packages added
        :type  num_units: int
        """

        metadata_file_path = os.path.join(working_dir, REPO_DATA_DIR_NAME, PRIMARY_XML_FILE_NAME)
        self.num_packages = num_units
        attributes = {'xmlns': COMMON_NAMESPACE,
                      'xmlns:rpm': RPM_NAMESPACE,
                      'packages': str(self.num_packages)}
        super(PrimaryXMLFileContext, self).__init__(metadata_file_path, 'metadata',
                                                    search_tag='package',
                                                    root_attributes=attributes,
                                                    checksum_type=checksum_type)

    def initialize(self):
        """
        Initialize all the file handles and fast forward the xml to the point where we should
        start adding content
        """
        super(PrimaryXMLFileContext, self).initialize()

    def add_unit_metadata(self, unit):
        """
        Add the metadata to primary.xml.gz for the given unit.

        :param unit: unit whose metadata is to be written
        :type  unit: pulp.plugins.model.Unit
        """

         if self.checksum_type == "sha256":
             label = "repodata"
         else:
             label = "repodata-%s" % self.checksum_type
         if label not in unit.metadata and "repodata" in unit.metadata:
             unit.metadata[label] = rpm_parse.get_package_xml(unit.storage_path,
                                                              sumtype=self.checksum_type,
                                                              changelog_limit=unit.metadata.get("changelog_limit", 10))
            metadata = {'label': unit.metadata[label]}
            content_manager = manager_factory.content_manager()
            content_manager.update_content_unit(unit_type_id, unit_id, metadata)

        metadata = unit.metadata[label]['primary']
        if isinstance(metadata, unicode):
            metadata = metadata.encode('utf-8')
        self.metadata_file_handle.write(metadata)
