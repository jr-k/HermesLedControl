import logging
from parameters import parameters

class ConfigManager:

	def __init__(self, currentSiteId):
		self._currentSiteId = currentSiteId
		self._logger = logging.getLogger('HermesLedControl')
		self._logger.info('Initializing ConfigManager')

	def has(self, key):
		return key in parameters

	def get(self, key, default=None):
		if self.has(key):
			value = parameters[key]

			return value

		if not default:
			self._logger.error(f"Configuration key '{key}' doesn't exist")

		return default

	def getSite(self, siteId):
		sites = self.get("sites", None)

		if not sites:
			return None

		return sites[siteId] if siteId in sites else None

	def getSiteAttribute(self, attribute, siteId=None, default=None):
		if siteId is None:
			siteId = self._currentSiteId

		site = self.getSite(siteId=siteId)

		if not site or attribute not in site:
			return default

		return site[attribute]

	def getCurrentSiteId(self):
		return self._currentSiteId
